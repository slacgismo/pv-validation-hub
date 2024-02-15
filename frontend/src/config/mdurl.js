// This file contains the functionality for replacing specific markdown image paths to work within the application.

const process = require('process');

function replaceImagePaths(markdown, analysis_id) {
    const regex = /!\[(.*?)\]\(\.\/(.*?)\)/g;
    return markdown.replace(regex, `![$1](${process.env.PUBLIC_URL}/assets/${analysis_id}/$2)`);
}

export default replaceImagePaths;