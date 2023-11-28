import { createSocket } from 'dgram';
require('dotenv').config()
import ClientData from './cache';

const { PORT, HOST } = process.env;

const server = createSocket('udp4');

const cache = new Map<number, ClientData>(); // port -> ClientData

server.on('listening', () => {
  const address = server.address();
  console.log('UDP Server listening on ' + address.address + ':' + address.port);
});

server.on('message', function(message, remote) {

	if (!cache.has(remote.port)) {
		cache.set(remote.port, new ClientData(remote.port));
	}

	const clientData = cache.get(remote.port);

	const arr = [];
	for (let i = 0; i < message.length; i += 4) {
		arr.push(message.readFloatLE(i));
	}

	// TODO - decode packet, which in the future might be keypresses
	
	clientData.update(arr);

  console.log(`\x1b[36mPacket from \x1b[33m${remote.port}:\x1b[0m ${arr}`);
});

server.bind(Number(PORT), HOST);