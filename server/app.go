package main

import (
	"go.uber.org/fx"
	"go.uber.org/zap"

	"github.com/Feresey/NNM/server/httpsrv"
)

func NewApp(conf *Config, logger *zap.Logger) *fx.App {
	return fx.New(
		fx.Supply(*conf, logger),
		fx.Provide(
			httpsrv.NewHTTPServer,
		),
		fx.Invoke(func(srv *httpsrv.Server) {}),
	)
}
