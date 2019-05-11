const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/emails', {useNewUrlParser: true});

const bodySchema = new mongoose.Schema({
  city: String,
  body: String,
  emails: [String]
});

const Body = mongoose.model('Body', bodySchema);