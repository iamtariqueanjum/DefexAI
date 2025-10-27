# Node.js image
FROM node:20-alpine

# Set workdir
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy rest of app
COPY . .

# Build
RUN npm run build

# Expose frontend port
EXPOSE 3000

# Start Next.js
CMD ["npm", "start"]
