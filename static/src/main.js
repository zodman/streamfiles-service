let WebTorrent = require("webtorrent")

if (WebTorrent.WEBRTC_SUPPORT) {
    console.log("supported");
}

client = new WebTorrent();
var protocol = window.location.protocol.replace("http", "ws")
trackers = [
    `${protocol}//${window.location.hostname}:8080/`
]
const torrentUrl = `${window.location.protocol}//${window.location.host}/torrent/`;

console.log("trackers", trackers, 'url',  torrentUrl);
client.add(torrentUrl,{'announce': trackers},(torrent) =>{
    console.log("loaded", torrent.numPeers, 'peers', torrent);
    let file = torrent.files[0];
    if (file) {
        file.appendTo('.torrent',{autoplay:true});
    }
});


client.on('torrent', t => {
        console.log("on torrent", t);
        let url =`${window.location.protocol}//${window.location.host}/download/otome-1.mp4?wiii=1`;
        t.addWebSeed(url);
});



client.on("error", (e) =>{
    console.log("client error", e);
});

window.client=client
