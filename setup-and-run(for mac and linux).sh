#!/usr/bin/env bash
set -euo pipefail

step() {
  printf "\n==== %s ====\n\n" "$1"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

OS="$(uname -s)"

step "Detecting operating system"
echo "Detected: $OS"

# ----------------------------
# Install Node.js (includes npm)
# ----------------------------
step "Installing Node.js LTS if needed"
if command_exists node && command_exists npm; then
  echo "Node already installed: $(node -v)"
  echo "npm already installed: $(npm -v)"
else
  if [[ "$OS" == "Darwin" ]]; then
    if ! command_exists brew; then
      echo "Homebrew not found. Installing Homebrew..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      if [[ -x /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
      elif [[ -x /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
      fi
    fi

    brew update
    brew install node
  else
    # Linux
    if command_exists apt-get; then
      sudo apt-get update
      sudo apt-get install -y nodejs npm
    elif command_exists dnf; then
      sudo dnf install -y nodejs npm
    elif command_exists yum; then
      sudo yum install -y nodejs npm
    elif command_exists pacman; then
      sudo pacman -Sy --noconfirm nodejs npm
    else
      echo "Unsupported Linux package manager. Install Node.js manually."
      exit 1
    fi
  fi
fi

step "Verifying Node.js and npm"
node -v
npm -v

# ----------------------------
# Install MongoDB
# ----------------------------
step "Installing MongoDB Community Server if needed"
if command_exists mongod; then
  echo "mongod already installed."
else
  if [[ "$OS" == "Darwin" ]]; then
    if ! command_exists brew; then
      echo "Homebrew is required on macOS."
      exit 1
    fi
    brew tap mongodb/brew
    brew install mongodb-community@8.0
  else
    # Linux
    # Generic best-effort path. MongoDB officially provides distro-specific install docs.
    if command_exists apt-get; then
      echo "MongoDB on Ubuntu/Debian should preferably be installed from MongoDB's official repo."
      echo "This script will try distro packages first."
      sudo apt-get update
      sudo apt-get install -y mongodb || sudo apt-get install -y mongodb-org || true
    elif command_exists dnf; then
      sudo dnf install -y mongodb-org || sudo dnf install -y mongodb || true
    elif command_exists yum; then
      sudo yum install -y mongodb-org || sudo yum install -y mongodb || true
    elif command_exists pacman; then
      sudo pacman -Sy --noconfirm mongodb
    else
      echo "Unsupported Linux package manager. Install MongoDB manually."
      exit 1
    fi
  fi
fi

# ----------------------------
# Start MongoDB
# ----------------------------
step "Starting MongoDB"
if command_exists brew && [[ "$OS" == "Darwin" ]]; then
  brew services start mongodb/brew/mongodb-community@8.0 || true
elif command_exists systemctl; then
  sudo systemctl start mongod || sudo systemctl start mongodb || true
elif command_exists service; then
  sudo service mongod start || sudo service mongodb start || true
fi

# Fallback
if ! pgrep -x mongod >/dev/null 2>&1; then
  echo "MongoDB service did not start automatically."
  echo "Trying to launch mongod directly in background..."
  mkdir -p ./mongodb-data
  nohup mongod --dbpath ./mongodb-data --bind_ip 127.0.0.1 --port 27017 >/tmp/mongod.log 2>&1 &
  sleep 5
fi

# ----------------------------
# Create .env
# ----------------------------
step "Creating .env if needed"
if [[ ! -f ".env" ]]; then
  if [[ -f ".env.example" ]]; then
    cp .env.example .env
    echo ".env created from .env.example"
  else
    echo ".env.example not found. Create .env manually."
  fi
else
  echo ".env already exists."
fi

# ----------------------------
# Install project deps and run
# ----------------------------
step "Installing project dependencies"
npm install

step "Running database seed"
npm run seed

step "Starting development server"
npm run dev