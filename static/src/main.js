let WebTorrent = require("webtorrent")

if (WebTorrent.WEBRTC_SUPPORT) {
    console.log("supported");
}

client = new WebTorrent();
trackers = [
    "wss://tracker.btorrent.xyz",
    "wss://tracker.openwebtorrent.com",
    "wss://tracker.fastcast.nz",
    "wss://tracker.fastcast.nz/"
]
const torrentUrl = "http://localhost:8000/torrent/";

client.add(torrentUrl,{'announce': trackers},(torrent) =>{
    console.log("loaded", torrent.numPeers, 'peers', torrent);
    let file = torrent.files[0];
    if (file) {
        file.appendTo('.torrent',{autoplay:true});
    }
});


client.on('torrent', t => {
        console.log("on torrent", t);
        let url ="http://localhost:8000/download/otome-1.mp4?wiii=1";
        t.addWebSeed(url);
});


client.on("error", (e) =>{
    console.log("client error", e);
});

