import pathlib

APP_NAME = "AFRE – Agentic Agri-Finance Risk Engine"
APP_TAGLINE = "Econometrics × ML × Policy × Finance"

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]

DEFAULT_RANDOM_STATE = 42

VOLATILITY_LOOKBACK_MONTHS = 36
CLIMATE_LOOKBACK_YEARS = 10
MIN_OBS_FOR_MODEL = 24
