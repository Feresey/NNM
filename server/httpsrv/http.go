package httpsrv

import (
	"context"
	"errors"
	"net/http"

	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	"github.com/rs/cors"
	"go.uber.org/fx"
	"go.uber.org/zap"
)

type Config struct {
	Addr       string
	ScriptPath string
}

type Server struct {
	c Config

	logger *zap.Logger
	srv    *http.Server
}

type In struct {
	fx.In
	LC   fx.Lifecycle
	Shut fx.Shutdowner

	Logger *zap.Logger
	Config Config
}

func NewHTTPServer(in In) *Server {
	srv := &Server{
		c:      in.Config,
		logger: in.Logger.Named("http"),
	}
	srv.initServer()

	in.LC.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			go func() {
				if err := srv.srv.ListenAndServe(); err != nil {
					if !errors.Is(err, http.ErrServerClosed) {
						srv.logger.Error("server stopped", zap.Error(err))
					} else {
						srv.logger.Info("server closed")
					}
					_ = in.Shut.Shutdown()
				}
			}()
			return nil
		},
		OnStop: func(ctx context.Context) error {
			return srv.srv.Shutdown(ctx)
		},
	})

	return srv
}

func (s *Server) initServer() {
	s.srv = &http.Server{
		Addr: s.c.Addr,
	}

	ccc := cors.Default()

	r := mux.NewRouter()
	r.Use(
		ccc.Handler,
		s.loggingMiddleware,
		func(h http.Handler) http.Handler {
			return handlers.RecoveryHandler(handlers.RecoveryLogger(zap.NewStdLog(s.logger)))(h)
		},
	)
	r.NotFoundHandler = http.HandlerFunc(s.loggingHandler(true))
	r.HandleFunc(`/labs`, s.labs)
	s.setAssets(r)

	s.srv.Handler = r
}

func (s *Server) loggingHandler(notFound bool) http.HandlerFunc {
	return http.HandlerFunc(func(rw http.ResponseWriter, r *http.Request) {
		msg := "request"
		if notFound {
			msg = "not found"
			defer http.NotFound(rw, r)
		}
		s.logger.Info(msg, zap.String("method", r.Method), zap.Stringer("url", r.URL))
	})
}

func (s *Server) loggingMiddleware(h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		s.loggingHandler(false)(w, r)
		h.ServeHTTP(w, r)
	})
}
