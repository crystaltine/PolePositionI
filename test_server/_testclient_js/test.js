const createRoomButton = document.getElementById('createroom')
const roomDisplay = document.getElementById('connectedroom')
const roomIdInput = document.getElementById('roomid')
const sendRoomId = document.getElementById('idsend')

// init handshake with server
let client_id;

fetch("http://localhost:4000/handshake")
.then(res => res.text())
.then(data => {
    console.log(`Initial handshake response: ${data.toString()}`);
    client_id = data
})

const socket = io.connect('http://localhost:3999', {query: `cid=${client_id}`});
console.log("socket thingy lol")

socket.onmessage = (data) => {
    const li = document.createElement('li');
	li.innerHTML = `Received: ${data}`
	document.getElementById('feed').appendChild(li);
}

createRoomButton.addEventListener('click', () => {
    fetch(`http://localhost:4000/createroom/${client_id}`)
    .then(res => res.json())
    .then(data => {
        console.log(`createroom response: ${JSON.stringify(data)}`)

        if (!data || !data.success || !data.code) {
            roomDisplay.innerHTML = "Unable to connect to a room!"
        } else {
            roomDisplay.innerHTML = `Connected to room with code <b>${data.code}</b>`
        }
    })
})