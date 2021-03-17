package main

import (
	"fmt"
	"os"

	"go.uber.org/fx"
	"sigs.k8s.io/yaml"

	"github.com/Feresey/NNM/server/httpsrv"
)

type Config struct {
	fx.Out

	HTTP httpsrv.Config `json:"http"`
}

func ParseConfig(path string) (*Config, error) {
	var raw []byte

	if path != "" && path != "-" {
		var err error
		raw, err = os.ReadFile(path)
		if err != nil {
			return nil, fmt.Errorf("read config file: %w", err)
		}
	}
	res := DefaultConfig()
	if err := yaml.Unmarshal(raw, res); err != nil {
		return nil, fmt.Errorf("unmarshal config file: %w", err)
	}
	return res, nil
}

func DefaultConfig() *Config {
	return &Config{
		HTTP: httpsrv.Config{
			Addr:       ":8080",
			ScriptPath: "httpsrv/labs/labs/labs.py",
		},
	}
}
