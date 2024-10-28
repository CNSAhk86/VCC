const WebSocket = require('ws');

let wsServer = new WebSocket.Server({ port: 3333 });

console.log('Server opened on port 3333.');

wsServer.on('connection', function connection(client) {
    console.log('Client connected');
    // console.log(Number of connected clients: ${wsServer.clients.size});

    client.on('message', function mss(message) {
        console.log('client: %s', message);

        // 메시지를 보낸 클라이언트를 제외한 모든 클라이언트에게 메시지를 전송함
        wsServer.clients.forEach(function each(ws) {
            if (ws !== client && ws.readyState === WebSocket.OPEN) {
                ws.send(message.toString()); // 메시지를 문자열로 변환하여 전송함 (안그러면 b'Trigger Sign'이라고 뜸)
            }
        });
    });

    client.on('close', function () {
        console.log('Client disconnected');
        // console.log(Number of connected clients: ${wsServer.clients.size});
    });

    client.on('error', function (error) {
        console.error('WebSocket error:', error);
    });
});

wsServer.on('error', function (error) {
    console.error('Server error:', error);
});