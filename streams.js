const execFile = require('child_process').execFile;
const fs = require('fs');


const getURL = function(url, file) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https') ? require('https') : require('http');
    const request = lib.get(url, (response) => {
      if (response.statusCode != 200) {
         reject(new Error('Failed to load URL, status code: ' + response.statusCode));
       }
      if (file) {
        var writeStream = fs.createWriteStream(file);
        response.pipe(writeStream);
      } 
      const body = [];
      response.on('data', (chunk) => body.push(chunk));
      response.on('end', () => {
        console.log("gotURL %s",url);
        resolve(body.join(''));
      });
    });
    request.on('error', (err) => reject(err))
    })
};

// Take a URL such as https://www.twitch.tv/nalcs1
const extractURLs = function (url) {
  return new Promise((resolve, reject) => {
    var data = null;

    const child = execFile(
      'livestreamer', [
        '--twitch-oauth-token',
        'kjjw1gc93wudbhbkay5m5jkm0azrp4',
        url,
        '--json'
      ], (error, stdout, stderr) => {
        if (error) {
          reject(error);
        }
        data = JSON.parse(stdout);
        if (data.error) {
          reject(data.error);
        } else {
          //console.log(data.streams);
          resolve({
            video: data.streams['best'].url
            });
        }
      });
  });
}

extractURLs("https://www.twitch.tv/canadianparalympic")
.then (stream => {
  baseURL = stream.video.match(/.*\//g);
  getURL(stream.video) // m3u8
  .then(data => {
    console.log("\n\n**** VIDEO *****\n",data);
    // allChunks = data.match(/.*\.ts/g);
    // allChunks.forEach(chunk => {
    //  console.log("chunk: ->",chunk,"<-");
    //  getURL(baseURL + chunk, chunk);
    //})
  })
  .catch(err => console.log(err));
  // getURL(stream.audio)
  // .then(data => console.log("\n\n**** AUDIO *****\n",data))
  // .catch(err => console.log(err));
})
.catch(err => console.log(err));

// TO DO
// use the base URL from the m3u8 to track chunks every few seconds
// create an associative array with all the chunks


