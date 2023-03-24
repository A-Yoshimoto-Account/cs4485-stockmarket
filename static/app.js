function updateKSimValue() {
    let newKSim = document.getElementById('kSimRange').value;
    document.querySelector("span[label='kSimLabel']").innerHTML = newKSim;
}
function updateMemoryValue() {
    let newMemoryVal = document.getElementById('memoryRange').value;
    document.querySelector("span[label='memoryLabel']").innerHTML = newMemoryVal;
}

/*
Connected to Submit button

*/
function updateTextArea() {
	let data = {
		'question': document.querySelector("input[name='question']").value,
		'ksim': document.getElementById('kSimRange').value,
		'memory': document.getElementById('memoryRange').value,
	};
	document.querySelector("input[name='question']").value = '';
	console.log(data);
	const url = '/process_question';
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
	queryDivs = document.getElementsByClassName("user-queries")
	responseDivs = document.getElementsByClassName("model-responses");
	rows = '';
	Array.from(queryDivs).forEach((queryDiv, index) => {
		responseDiv = responseDivs[index];
		query = queryDiv.getElementsByTagName('p')[0].innerHTML;
		response = responseDiv.getElementsByTagName('p')[0].innerHTML;
		rows += query + ',' + response;
		if (index < queryDivs.length - 1) {
			rows += '\n';
		}
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

/**
 * Reads the file stored in the file input and sends its text content to the
 * 	/upload_convo endpoint.
 * The expected file is a CSV with the format: "question,answer"
 * Receives a response JSON object with a message type, message, and a boolean indicating success/failure.
 * On success, the text area is replaced with the contents of the file.
 * On failure, it will not populate the text area at all.
 * The system message will be appended at the end of the text area.
 * 
 * @returns null
 */
function uploadSavedConvo() {
    const convoFile = document.getElementById("savedConvoFile").files[0];
	// does nothing if no file exists
	if (convoFile == null) {
		return;
	}
	document.getElementById("savedConvoFile").value = '';

	let csvReader = new FileReader();
	csvReader.onload = function() {
		// retrieve text of file
		const fileText = csvReader.result
		const url = '/upload_convo';
		fetch(
			url, 
			{
				'method': 'POST',
				'headers': {'Content-Type': 'application/json'},
				'body': JSON.stringify(fileText)
			}
		).then(response => response.json())
		.then(resp => {
			let chatArea = document.getElementById('chat-area');
			// on success, populate text area with file's contents
			if (resp['ok']) {
				chatArea.innerHTML = '';
				rows = fileText.split('\n');
				rows.forEach((row) => {
					content = row.split(',');
					chatArea.innerHTML += createConvoElement(content[0], content[1]);	
				})
			}
			// append the system message
			chatArea.innerHTML += createSystemMessage(resp['type'], resp['message']);
			chatArea.scrollTop = chatArea.scrollHeight;
		})
	}
	csvReader.readAsText(convoFile);
    console.log("Sent " + convoFile.name + " as convo memory");
}

function clearMemory() {
    console.log("Clears the interval convo memory")
}

function clearAll() {
    console.log("Clears the screen and the internal convo memory");
}
/**
 * Takes in a system message type and a system message to
 * 	return HTML for a system message block in the text area
 * @param {String} type 
 * @param {String} message 
 * @returns String
 */
function createSystemMessage(type, message) {
	return 	'<div class="system-message">' + 
			'	<div class="system-messages ' + type + ' text-block">' + 
			'		<b>System:&nbsp</b><p>' + message + '</p>' +
			'	</div>' + 
			'</div>';
}
/**
 * Takes in a question and answer to
 * 	return HTML for a QA block in the text area
 * @param {String} question 
 * @param {String} answer 
 * @returns String
 */
function createConvoElement(question, answer) {
	return 	'<div class="query-response">' + 
			'	<div class="user-queries text-block">' + 
			'		<b>You:&nbsp</b><p>' + question + '</p>' +
			'	</div>' + 
			'	<div class="model-responses text-block">' + 
			'		<b>Response:&nbsp</b><p>' + answer + '</p>' + 
			'	</div>' + 
			'</div>';
}