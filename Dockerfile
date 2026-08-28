# the base image
FROM python:3.12-slim  

# prevents python from writing .pyc file and force unbuffered logging for cleaner stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \  
	PYTHONUNBUFFERED=1 

# working directory inside the container
WORKDIR /app 

# copy dependency files only 
COPY requirements.txt . 

# install the dep and the --no-cache-dir keeps the image light
RUN pip install --no-cache-dir -r requirements.txt 

# copy the rest of the codebase 
COPY . . 

# create a non-root user and transfer ownership of /app
RUN useradd -m appuser && chown -R appuser:appuser /app 
USER appuser

EXPOSE 8082

# command to run the app (binds dynamically to cloud $PORT or defaults to 8082)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8082}"]