from backend.providers.registry import provider_status
from backend.security.secrets import secret_status
from backend.security.api_auth import api_auth_required, api_token_configured


PRODUCTION_SECRETS=(
    "COZY_IMAGE_API_KEY",
    "COZY_VISION_API_KEY",
    "COZY_API_TOKEN",
)


def system_status():
    providers=provider_status()
    secrets=secret_status(PRODUCTION_SECRETS)
    return {
        "providers":[{"role":p.role,"provider":p.provider,"state":p.state,"detail":p.detail} for p in providers],
        "secrets":[{"name":s.name,"configured":s.configured} for s in secrets],
        "api_auth":{"required":api_auth_required(),"configured":api_token_configured()},
        "production_ready":all(p.state.value=="CONFIGURED" for p in providers) and (not api_auth_required() or api_token_configured()),
    }
