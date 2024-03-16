// This file contains the functionality for replacing specific markdown image paths
// to work within the application.

function replaceImagePaths(markdown, analysisId) {
  const regex = /!\[(.*?)\]\(\.\/(.*?)\)/g;
  return markdown.replace(regex, `![$1](${process.env.PUBLIC_URL}/assets/${analysisId}/$2)`);
}

export default replaceImagePaths;
