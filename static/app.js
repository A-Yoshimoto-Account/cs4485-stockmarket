function updateTextArea() {
	let data = {
		'question': document.querySelector("input[name='question']").value
	};
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

	let now = getDateTimeNow();	
	let filename = 'gpt3convo_' + now + '.csv'
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