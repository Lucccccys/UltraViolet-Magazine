const mongoose = require('mongoose');

async function connectToDatabase() {
  const mongoUri = process.env.MONGODB_URI;

  if (!mongoUri) {
    throw new Error('MONGODB_URI is not set.');
  }

  mongoose.set('strictQuery', true);

  const safeUri = mongoUri.replace(/\/\/([^:]+):([^@]+)@/, '//***:***@');
  console.log('Using MongoDB URI:', safeUri);

  await mongoose.connect(mongoUri, {
    autoIndex: true
  });

  console.log('Connected to MongoDB');
  console.log('Mongo host:', mongoose.connection.host);
  console.log('Mongo db name:', mongoose.connection.name);
}

module.exports = { connectToDatabase };
