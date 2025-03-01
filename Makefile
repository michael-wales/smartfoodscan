default: pylint pytest

install-dev:
	pip install -e .
	pip install -r requirements-dev.txt

install:
	pip install -r requirements.txt

pylint:
	@find . -iname "*.py" -not -path "./tests/*" | xargs -n1 -I {}  pylint --output-format=colorized {}; true

pytest:
	@PYTHONDONTWRITEBYTECODE=1 pytest -v --color=yes


#########
### DOCKER LOCAL
#########

build_container_local:
	docker build --tag=$$IMAGE:deve .

run_container_local:
	docker run -it -e PORT=8000 -p 8000:8000 $$IMAGE:deve


#########
## DOCKER DEPLOYMENT
#########

### (RUN ONLY ONCE)
allow_docker_push:
	gcloud auth configure-docker $$GCP_REGION-docker.pkg.dev

create_artifacts_repo:
	gcloud artifacts repositories create $$ARTIFACTSREPO --repository-format=docker \
	--location=$$GCP_REGION --description="Repository for storing images"

# For Apple silicon chips:
m1_build_image_production:
	docker build --platform linux/amd64 -t $$GCP_REGION-docker.pkg.dev/$$GCP_PROJECT/$$ARTIFACTSREPO/$$IMAGE:prod .

# For everything else:
build_for_production:
	docker build -t $$GCP_REGION-docker.pkg.dev/$$GCP_PROJECT/$$ARTIFACTSREPO/$$IMAGE:prod .

push_image_production:
	docker push $$GCP_REGION-docker.pkg.dev/$$GCP_PROJECT/$$ARTIFACTSREPO/$$IMAGE:prod
###

deploy_to_cloud_run:
	gcloud run deploy --image $$GCP_REGION-docker.pkg.dev/$$GCP_PROJECT/$$ARTIFACTSREPO/$$IMAGE:prod --memory $$MEMORY --region $$GCP_REGION
