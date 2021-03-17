package main

import (
	"flag"
	"fmt"
	"os"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

func exitf(format string, args ...interface{}) {
	fmt.Fprintf(os.Stderr, format, args...)
	os.Exit(1)
}

func main() {
	cc := flag.String("config", "-", "path to config file")
	flag.Parse()

	conf, err := ParseConfig(*cc)
	if err != nil {
		exitf("Failed to load config: %v", err)
	}

	lc := zap.NewDevelopmentConfig()
	lc.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder

	logger, err := lc.Build()
	if err != nil {
		exitf("Failed to initialize logger: %v", err)
	}

	app := NewApp(conf, logger)
	app.Run()
}
