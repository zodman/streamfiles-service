const byteSize = require("byte-size")

export default () => ({
    done: '',
    progress:'',
    downloadSpeed:'',
    uploadSpeed: '',
    torrent:{},
    init(){
        let self = this;
        setInterval(()=>{
            if (window.torrent) {
                self.torrent = window.torrent
                self.done = window.torrent.done ? 'Yes' : 'No'
                self.progress = Math.ceil(window.torrent.progress*100)
                self.uploadSpeed = `${byteSize(window.torrent.uploadSpeed)}/sec`
                self.downloadSpeed = `${byteSize(window.torrent.downloadSpeed)}/sec`
            }
        }, 1000);
    }
})
