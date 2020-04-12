chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
  if (tab.url.startsWith("https://www.amazon.")) {
    if (changeInfo.status == "complete") {
      chrome.tabs.executeScript({ file: 'change.js', allFrames: false });
    };
  };
});

