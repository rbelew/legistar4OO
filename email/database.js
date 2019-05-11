const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/emails', {useNewUrlParser: true});

const emailSchema = new mongoose.Schema({
  city: String,
  emails: [String]
});

const City = mongoose.model('City', emailSchema);