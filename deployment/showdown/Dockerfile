FROM node:22-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone Pokemon Showdown
RUN git clone https://github.com/smogon/pokemon-showdown.git .

RUN npm install

# RUN cp config/config-example.js config/config.js

# RUN npm run build

# Expose the default port
EXPOSE 8000

# Start the server with no security (for bot access)
CMD ["node", "pokemon-showdown", "start", "--no-security"]
