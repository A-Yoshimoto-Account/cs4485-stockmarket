function updateKSimValue() {
    let newKSim = document.getElementById('kSimRange').value;
    document.querySelector("span[label='kSimLabel']").innerHTML = newKSim;
}
function updateMemoryValue() {
    let newMemoryVal = document.getElementById('memoryRange').value;
    document.querySelector("span[label='memoryLabel']").innerHTML = newMemoryVal;
}

// Submit key function
function updateTextArea() {
	let data = {
		'question': document.querySelector("input[name='question']").value,
		'ksim': document.getElementById('kSimRange').value,
		'memory': document.getElementById('memoryRange').value,
	};
	console.log(data);

	//Sets endpoint
	const url = '/process_question';
	
	//calls the endpoint
	fetch(url, {
		'method': 'POST',
		'headers': {'Content-Type': 'application/json'},
		'body': JSON.stringify(data)
	})
		.then(response => response.json())
		.then(data => {
			let html = 
				'<div class="query-response">' + 
				'	<div class="user-queries text-block">' + 
				'		<b>You:&nbsp</b><p>' + data['question'] + '</p>' +
				'	</div>' + 
				'	<div class="model-responses text-block">' + 
				'		<b>Response:&nbsp</b><p>' + data['answer'] + '</p>' + 
				'	</div>' + 
				'</div>';
			let chatArea = document.getElementById('chat-area');
			chatArea.innerHTML += html;
			chatArea.scrollTop = chatArea.scrollHeight;
		})
}

function downloadConvo() {
	let type = {type: 'text/csv;charset=utf-8'};
	let data = getConversation();
	let file = new Blob([data], type=type);
	let modelName = document.getElementById('modelName').innerHTML;
	let now = getDateTimeNow();	
	let filename = modelName + '_' + now + '.csv'
	let url = URL.createObjectURL(file);

	let downloadLink = document.createElement('a');

	downloadLink.href = url;
	downloadLink.download = filename;

	document.body.appendChild(downloadLink);
	downloadLink.click();
	document.body.removeChild(downloadLink);

}
function getConversation() {
	let rows = 'query,response\n'
	queryDivs = document.getElementsByClassName("user-queries")
	responseDivs = document.getElementsByClassName("model-responses");
	Array.from(queryDivs).forEach((queryDiv, index) => {
		responseDiv = responseDivs[index];
		query = queryDiv.getElementsByTagName('p')[0].innerHTML;
		response = responseDiv.getElementsByTagName('p')[0].innerHTML;
		rows += query + ',' + response + '\n';
	});

	return rows;
}
function getDateTimeNow() {
	let d = new Date(Date.now());
	year = d.getFullYear();
	month = d.getMonth();
	day = d.getDate();
	hour = d.getHours();
	minute = d.getMinutes();
	seconds = d.getSeconds();

	return year + '-' + month + '-' + day + '_' + hour + ':' + minute + ':' + seconds;
}

function uploadSavedConvo() {
    console.log("Upload a saved convo CSV as memory");
}

function clearMemory() {
	console.log("Clears the internal convo memory");

	//Clears internal memory using 'clear_memory()'
	const url = '/clear_memory';
	fetch(url, {
		'method': 'POST',
		'headers': {'Content-Type': 'application/json'}
	})
	let html = 
				'<div class="system-message">' + 
				'	<div class="system-messages text-block">' + 
				'		<b>System:&nbsp</b><p>Your Current Conversation Memory has been cleared.</p>' +
				'	</div>' +
				'</div>';
			let chatArea = document.getElementById('chat-area');
			chatArea.innerHTML += html;
			chatArea.scrollTop = chatArea.scrollHeight;
	
}

function clearAll() {
    console.log("Clears the screen and the internal convo memory");

	//Clears internal memory using same function as 'clearMemory()'
	const url = '/clear_memory';
	fetch(url, {
		'method': 'POST',
		'headers': {'Content-Type': 'application/json'}
	})

	//informs user that entire conversation has been cleared with 5 second popup.
	let chatArea = document.getElementById('chat-area');
	chatArea.innerHTML = "";
	let html = 
				'<div class="system-message">' + 
				'	<div class="system-messages text-block">' + 
				'		<b>System:&nbsp</b><p>Your Entire Conversation has been cleared.</p>' +
				'	</div>' +
				'</div>';
	chatArea.innerHTML += html;
	chatArea.scrollTop = chatArea.scrollHeight;
	setTimeout(function() {document.getElementById('chat-area').innerHTML = '';} , 5000);
}