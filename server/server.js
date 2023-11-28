"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var dgram_1 = require("dgram");
require('dotenv').config();
var _a = process.env, PORT = _a.PORT, HOST = _a.HOST;
var server = (0, dgram_1.createSocket)('udp4');
server.on('listening', function () {
    var address = server.address();
    console.log('UDP Server listening on ' + address.address + ':' + address.port);
});
server.on('message', function (message, remote) {
    var arr = [];
    for (var i = 0; i < message.length; i += 4) {
        arr.push(message.readFloatLE(i));
    }
    console.log("\u001B[36mPacket from \u001B[33m".concat(remote.port, ":\u001B[0m ").concat(arr));
    //const newMessage = `Echo: ${message}`;
    /*server.send(newMessage, 0, newMessage.length, remote.port, remote.address, (err, bytes) => {
        if (err) console.log('error while sending back to client: ', err);
      console.log('UDP message sent to ' + remote.address +':'+ remote.port);
    });*/
});
server.bind(Number(PORT), HOST);
