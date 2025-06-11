FROM public.ecr.aws/lambda/python:3.11

ENV HOSTNAME="text-extractor"
ENV EXTERNAL_PORT="6000"
ENV PROXY_PARAMS="--enable-async"
ENV STARTUP_CMD="app.text_extractor.handler"

# Copy function code
# Will be overridden locally
COPY text-extractor ${LAMBDA_TASK_ROOT}/app

# Install system dependencies including build tools
RUN yum install -y \
    poppler-utils \
    gcc \
    gcc-c++ \
    python3-devel \
    && yum clean all


# Install the required packages
RUN pip install -r app/requirements.txt

# Copy lambda-proxy
COPY lambda-proxy /proxy

# Install packages required by lambda-proxy
RUN pip install -r /proxy/requirements.txt

# Set the custom entrypoint to run lambda-proxy on startup
ENTRYPOINT /proxy/startup.sh
