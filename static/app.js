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

// Prevent empty submissions
function submitForm(event) {
    event.preventDefault();
    var inputField = document.querySelector(".query-text");
    if (inputField.value.trim() !== "") {
        // Submit the form
        document.getElementById("send-query-form").onsubmit();
    } else {
        // Do nothing or show an error message
    }
}
// Submit key function
function updateTextArea() {
	// constants for button disabling
	const form = document.querySelector('#send-query-form');
	const subButton = form.querySelector('input[type="submit"]'); 
	const downloadButton = document.getElementById('downBut');
	const chooseFileButton = document.getElementById('savedConvoFile');
	const uploadButton = document.getElementById('uploadBut');
	const clearMemButton = document.getElementById('clearMemBut');
	const clearAllButton = document.getElementById('clearAllBut');

	// Disable Button
	subButton.disabled = true;
	downloadButton.disabled = true;
	chooseFileButton.disabled = true;
	uploadButton.disabled = true;
	clearMemButton.disabled = true;
	clearAllButton.disabled = true;

	// show spinner
	document.getElementById("spinner").style.visibility="visible";
	// gather arguments for endpoints
	let data1 = {
		'question': document.querySelector("input[name='question']").value,
	};
	let data2 = {
		'question': document.querySelector("input[name='question']").value,
		'ksim': document.getElementById('kSimRange').value,
		'memory': document.getElementById('memoryRange').value,
	};
	document.querySelector("input[name='question']").value = '';
	console.log(data2);

	//Sets endpoint
	const url1 = 'post_user_question';
	const url2 = '/process_question';
	
	//calls the endpoints
	// first endpoint returns the question
	fetch(url1, {
		'method': 'POST',
		'headers': {'Content-Type': 'application/json'},
		'body': JSON.stringify(data1)
	})
		.then(response => response.json())
		.then(data => {
			let html = 
				'<div class="query-response">' + 
				'	<div class="user-queries text-block">' + 
				'		<b>You:&nbsp</b><p>' + data['question'] + '</p>' +
				'	</div>' +
				'</div>';
			let chatArea = document.getElementById('chat-area');
			chatArea.innerHTML += html;
			chatArea.scrollTop = chatArea.scrollHeight;
			// then the second endpoint returns the answer
			return 	fetch(url2, {
				'method': 'POST',
				'headers': {'Content-Type': 'application/json'},
				'body': JSON.stringify(data2)
			})
				.then(response => response.json())
				.then(data => {
					let html = 
						'	<div class="model-responses text-block">' + 
						'		<b>Response:&nbsp</b><p>' + data['answer'] + '</p>' + 
						'	</div>' + 
						'</div>';
					let chatArea = document.getElementById('chat-area');
					chatArea.innerHTML += html;
					if ('error' in data) {
						chatArea.innerHTML += createSystemMessage('error', data['error']);
					}
					chatArea.scrollTop = chatArea.scrollHeight;

					// Re-enable button
					subButton.disabled = false;
					downloadButton.disabled = false;
					chooseFileButton.disabled = false;
					uploadButton.disabled = false;
					clearMemButton.disabled = false;
					clearAllButton.disabled = false;

					// hide spinner
					document.getElementById("spinner").style.visibility="hidden";
				})
		})
}
/**
 * creates a CSV file of the text area conversation and download it to the user's browser
 */
function downloadConvo() {
	let type = {type: 'text/csv;charset=utf-8'};
	// get CSV string
	let data = getConversation();
	// create CSV file
	let file = new Blob([data], type=type);
	let modelName = document.getElementById('modelName').innerHTML;
	let now = getDateTimeNow();
	// make file name
	let filename = modelName + '_' + now + '.csv'
	// create URL to click to download
	let url = URL.createObjectURL(file);

	let downloadLink = document.createElement('a');

	downloadLink.href = url;
	downloadLink.download = filename;

	document.body.appendChild(downloadLink);
	// click link to download
	downloadLink.click();
	document.body.removeChild(downloadLink);
}
/**
 * @returns the text area conversation as a CSV string
 */
function getConversation() {
	queryDivs = document.getElementsByClassName("user-queries")
	responseDivs = document.getElementsByClassName("model-responses");
	rows = '';
	// iterate through each query and response div in the text area
	Array.from(queryDivs).forEach((queryDiv, index) => {
		responseDiv = responseDivs[index];
		query = formatCSVString(queryDiv.getElementsByTagName('p')[0].innerHTML);
		response = formatCSVString(responseDiv.getElementsByTagName('p')[0].innerHTML);
		rows += `${query},${response}`
		if (index < queryDivs.length - 1) {
			rows += '\n';
		}
	});

	return rows;
}
/**
 * @returns The current time as a string
 */
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
 * Formats the input string to replace any quotations with \" and surround with double quotes
 * @param {String} s String to format
 */
function formatCSVString(s) {
	return `"${s.replace(/"/g, '\\"')}"`;
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
		const fileText = csvReader.result;
		console.log(fileText);
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
				rows = resp['content']
				rows.forEach((row) => {
					chatArea.innerHTML += createConvoElement(row['question'], row['answer']);	
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
	setTimeout(function() {document.getElementById('chat-area').innerHTML = '';} , 2500);
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

// This is the code that runs when the page loads
window.addEventListener("load", function() {
	document.getElementById("spinner").style.visibility = "hidden";
  });