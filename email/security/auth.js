
const config = require('./config/config.json');

const bcrypt = requre('bcrypt');

function authenticate(body, signature){
    var bodyString = JSON.stringify(body);
    const value = bcrypt.compare(bcrypt.hash(bodyString + config.hash_secret), signature);
    return value;
}