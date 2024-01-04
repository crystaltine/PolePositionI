const socket = io('http://localhost:3999');
console.log("socket thingy lol")

socket.onmessage = (data) => {
    const li = document.createElement('li');
	li.innerHTML = `Received: ${data}`
	document.getElementById('feed').appendChild(li);
}