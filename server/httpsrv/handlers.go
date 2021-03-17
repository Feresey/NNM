package httpsrv

import (
	"net/http"
	"os/exec"
	"strconv"

	"go.uber.org/zap"
)

func (s *Server) labs(w http.ResponseWriter, r *http.Request) {
	labID := r.FormValue("lab_id")

	_, err := strconv.Atoi(labID)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		s.logger.Error("failed to get lab ID", zap.String("raw", labID), zap.Error(err))
		return
	}

	cmd := exec.CommandContext(r.Context(), s.c.ScriptPath, labID)
	cmd.Stdin = r.Body
	cmd.Stdout = w

	if err := cmd.Run(); err != nil {
		s.logger.Error("failed to run lab", zap.Error(err))
		w.WriteHeader(http.StatusInternalServerError)
	}
}
