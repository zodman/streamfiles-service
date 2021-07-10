import Alpine from 'alpinejs'
import torrent from './torrent.js'

window.Alpine = Alpine
let WebTorrent = require("webtorrent")
if (WebTorrent.WEBRTC_SUPPORT) {
    //console.log("supported");
}

let client = new WebTorrent();
let trackers = [
    `${window.WS_SERVER}`
]
const torrentUrl = `${window.location.protocol}//${window.location.host}/torrent/${window.file}`;
//console.log("trackers", trackers, 'url',  torrentUrl);
client.add(torrentUrl,{'announce': trackers},(torrent) =>{
    //console.log("loaded", torrent.numPeers, 'peers', torrent);
    let file = torrent.files[0];
    if (file) {
        file.appendTo('.torrent',{autoplay:true});
    }
});


client.on('torrent', torrent => {
    //console.log("on torrent", torrent);
    file = torrent.files[0].name
    let url =`${window.location.protocol}//${window.location.host}/download/${file}`;
    torrent.addWebSeed(url);
    torrent.on('download', function (bytes) {
        window.torrent = torrent
    })
});

client.on("error", (e) =>{
    console.log("client error", e);
});

window.client=client
Alpine.data('torrent', torrent);
Alpine.start()
