var gPlots = [];
var gFirefoxId = null;
var gChromeId = null;
var gTitle = null;

function makeplot(firefoxId, chromeId, title) {
    gPlots = [];
    gFirefoxId = firefoxId;
    gChromeId = chromeId;
    gTitle = title;
    d3.csv("http://www.webpagetest.org/result/"+firefoxId+"/page_data.csv", function(data){ processData(data, true, title) } );
    d3.csv("http://www.webpagetest.org/result/"+chromeId+"/page_data.csv", function(data){ processData(data, false, title) } );
};

function processData(allRows, isFirefox, title) {
    var name = "Firefox run";
    var cname = "Firefox cached";
    var netColor = 'red';
    var cacheColor = 'orange';
    if (!isFirefox) {
        name = "Chrome run";
        cname = "Chrome cached"
        netColor = 'blue';
        cacheColor = 'cyan';
    }

    var net = { name: name, x: [], y: [], text: [], mode: 'markers', type: 'scatter', marker: { color: netColor }};
    var cache = { name: cname, x: [], y: [], text: [], mode: 'markers', type: 'scatter', marker: { color: cacheColor }};

    var tableColumn = document.getElementById('column').value;

    for (var i = 0; i < allRows.length; i++) {
        var row = allRows[i];

        var y = row[tableColumn];
        var x = row['Run'];
        var cached = parseInt(row['Cached']);
        var text = '';

        if (!cached) {
            net.x.push(x);
            net.y.push(y);
            // net.text.push(text);
        } else {
            cache.x.push(x);
            cache.y.push(y);
            // cache.text.push(text);
        }

    }

    gPlots.push(net);
    gPlots.push(cache);

    var layout = {
      title: title,
      xaxis: {
        title: 'run index',
        titlefont: {
          size: 18,
        }
      },
      yaxis: {
        title: tableColumn,
        titlefont: {
          size: 18,
        }
      }
    };

    if (gPlots.length == 4) {
        console.log(gPlots);
        Plotly.newPlot('myDiv', gPlots, layout);
    }
}

// makeplot('160104_M4_Q6H','160104_32_Q6K', 'test');

function createRow(domain, firefoxId, chromeId, firstSpeedIndex, cacheSpeedIndex) {
    var tr = document.createElement('tr');

    var td = document.createElement('td');
    var a = document.createElement('a');
    a.appendChild(document.createTextNode(domain));
    a.href = "#";
    a.onclick = function() {
        makeplot(firefoxId, chromeId, domain);
        return false;
    }
    td.appendChild(a);
    tr.appendChild(td);

    var td = document.createElement('td');
    var a = document.createElement('a');
    a.appendChild(document.createTextNode(firefoxId));
    a.href = "http://www.webpagetest.org/result/"+firefoxId+"/";
    td.appendChild(a);
    tr.appendChild(td);

    var td = document.createElement('td');
    var a = document.createElement('a');
    a.appendChild(document.createTextNode(chromeId));
    a.href = "http://www.webpagetest.org/result/"+chromeId+"/";
    td.appendChild(a);
    tr.appendChild(td);

    var td = document.createElement('td');
    td.appendChild(document.createTextNode(firstSpeedIndex));
    tr.appendChild(td);

    var td = document.createElement('td');
    td.appendChild(document.createTextNode(cacheSpeedIndex));
    tr.appendChild(td);

    return tr;
}

function computeTable(testData) {
    var div = document.createElement('div');
    div.classList.add('column');

    var table = document.createElement('table');

    var tr = document.createElement('tr');
    table.appendChild(tr);

    var td = document.createElement('td');
    td.appendChild(document.createTextNode(testData.name));
    tr.appendChild(td);

    var td = document.createElement('td');
    tr.appendChild(td);

    var td = document.createElement('td');
    tr.appendChild(td);

    /////////////

    var td = document.createElement('td');

    var a = document.createElement('a');
    a.appendChild(document.createTextNode('^'));
    a.href = '#';
    a.onclick = function() {
        testData.data.sort(function(a,b) {
            return a.firstDiff - b.firstDiff;
        });
        var newDiv = computeTable(testData);
        document.body.replaceChild(newDiv, div);
        return false;
    }
    td.appendChild(a);

    td.appendChild(document.createTextNode(' '));

    tr.appendChild(td);

    /////////////

    var td = document.createElement('td');

    var a = document.createElement('a');
    a.appendChild(document.createTextNode('^'));
    a.href = '#';
    a.onclick = function() {
        testData.data.sort(function(a,b) {
            return a.secondDiff - b.secondDiff;
        });
        var newDiv = computeTable(testData);
        document.body.replaceChild(newDiv, div);
        return false;
    }
    td.appendChild(a);

    tr.appendChild(td);

    /////////////

    for (var i = 0; i<testData.data.length; i++) {
        var entry = testData.data[i];
        table.appendChild(createRow(entry.domain, entry.firefoxId, entry.chromeId, entry.firstDiff, entry.secondDiff));
    }

    div.appendChild(table);
    return div;
}

function displayTable(testData) {
    var div = computeTable(testData);
    document.body.appendChild(div);
}


