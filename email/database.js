const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/emails', {useNewUrlParser: true});

const bodySchema = new mongoose.Schema({
  city: String,
  body: String,
  emails: [String]
});

const Body = mongoose.model('Body', bodySchema);

const addBody = (city, body, emails, callback) => {
  let body = new Body({ city, body, emails });
  body.save((err, body) => {
    if (err) callback(err);
  })
}

