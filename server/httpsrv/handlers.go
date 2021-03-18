package httpsrv

import (
	"bytes"
	_ "embed"
	"fmt"
	"html/template"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strconv"

	"github.com/Masterminds/sprig/v3"
	"github.com/gorilla/mux"
	"go.uber.org/zap"
)

func (s *Server) setHandlers(r *mux.Router) {
	r.HandleFunc(`/labs`, s.labs)
	r.HandleFunc(`/labs/lab5`, s.labHandler(5))
	s.setAssets(r)
}

func (s *Server) labs(w http.ResponseWriter, r *http.Request) {
	labID := r.FormValue("lab_id")

	_, err := strconv.Atoi(labID)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		s.logger.Error("failed to get lab ID", zap.String("raw", labID), zap.Error(err))
		return
	}

	var resp bytes.Buffer
	var errBuf bytes.Buffer

	cmd := exec.CommandContext(r.Context(), s.c.ScriptPath, labID)
	cmd.Stdin = io.TeeReader(r.Body, os.Stdout)
	cmd.Stdout = &resp
	cmd.Stderr = &errBuf

	if err := cmd.Run(); err != nil {
		s.logger.Error("failed to run lab", zap.Error(err))
		w.WriteHeader(http.StatusInternalServerError)
		_, _ = errBuf.WriteTo(w)
	}

	_, _ = resp.WriteTo(w)
}

var (
	//go:embed fuck/index.html.tpl
	indexTpl string
	// embed fuck/labs
	labsSrc = http.Dir("httpsrv")
)

func (s *Server) newIndexTemplate() error {
	tpl, err := template.New("lab").
		Funcs(sprig.HtmlFuncMap()).
		Parse(indexTpl)
	if err != nil {
		return fmt.Errorf("parse root template: %w", err)
	}
	s.indexTpl = tpl
	return nil
}

type labFiles struct {
	HTMLContent template.HTML
	Script      template.JS
}

func readFile(fs http.FileSystem, path string) ([]byte, error) {
	file, err := fs.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	return io.ReadAll(file)
}

func (s *Server) labHandler(labID int) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		fileBasename := fmt.Sprintf("fuck/labs/lab%d", labID)
		htmlSource, err := readFile(labsSrc, fileBasename+".html")
		if err != nil {
			s.logger.Error("failed to read html source", zap.Error(err))
			http.NotFound(w, r)
		}
		jsSource, err := readFile(labsSrc, fileBasename+".js")
		if err != nil {
			s.logger.Error("failed to read js source", zap.Error(err))
			http.NotFound(w, r)
		}
		lf := &labFiles{
			HTMLContent: template.HTML(htmlSource),
			Script:      template.JS(jsSource),
		}

		if err := s.indexTpl.Execute(w, lf); err != nil {
			s.logger.Error("failed to execute template", zap.Error(err))
		}
	}
}
