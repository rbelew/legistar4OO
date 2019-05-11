const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/emails', {useNewUrlParser: true});

const citySchema = new mongoose.Schema({
  city: String,
  bodies: [{body: String, emails: [String]}]
});

const City = mongoose.model('City', citySchema);