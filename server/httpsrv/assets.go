package httpsrv

import (
	"embed"
	"io/fs"
	"net/http"

	assetfs "github.com/elazarl/go-bindata-assetfs"
	"github.com/gorilla/mux"
)

//go:embed dist/front
var assets embed.FS

func (s *Server) setAssets(r *mux.Router) {
	// fs.WalkDir(assets, ".", func(path string, d fs.DirEntry, err error) error {
	// 	if err != nil {
	// 		return err
	// 	}

	// 	s.logger.Debug(path)

	// 	return nil
	// })

	r.PathPrefix(`/app`).Handler(http.StripPrefix("/app", http.FileServer(
		&assetfs.AssetFS{
			Asset: assets.ReadFile,
			AssetDir: func(path string) (names []string, err error) {
				entries, err := assets.ReadDir(path)
				if err != nil {
					return nil, err
				}
				for _, entry := range entries {
					names = append(names, entry.Name())
				}
				return names, nil
			},
			AssetInfo: func(path string) (fs.FileInfo, error) {
				file, err := assets.Open(path)
				if err != nil {
					return nil, err
				}
				return file.Stat()
			},
			Prefix:   "dist/front",
			Fallback: "index.html",
		},
	)))
}
