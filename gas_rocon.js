// auth
function authToken(token) {
    return token == getEnv("ACCESS_TOKEN");
}

// alias of doPost
function doGet(e) {
    return doPost(e);
}
  
// auth and parse data
function doPost(e) {
    let token = e.parameter.a_t;
  
    if(!authToken(token))
      return createResponseFormat("error", "invalid token");
    
    // get query type
    let action = e.parameter.sql;
    let param = e.parameter;
  
    let json;
    try {
      json = JSON.parse(e.postData.contents);
    } catch {
      json = {}
    }
  
    return doRouting(action, param);
}

// routing and return response data
// reduce eventcontainer entropy for testing more easily
function doRouting(action, param, json) {

    // add a new record
    if(action == "insert" || action == "INSERT") {
        table = param.table;
        col_list = param.cols.split(",");
        col_dict = {};
        for(let i = 0; i < col_list.length; i++) {
            col_dict[col_list[i].trim()] = param[col_list[i].trim()];
        }

        if(col_dict["id"] == undefined)
            col_dict["id"] = Utilities.getUuid();

        addRecord(table, col_dict);
        return createResponseSucceed();
    }
    
    // delete latest record
    if(action == "delete" || action == "DELETE") {
        table = param.table;
        where_col = param.w_col;
        where_op = param.w_op;
        where_val = param.w_val;

        deleteRecord(table, where_col, where_op, where_val);
        return createResponseSucceed();
    }
    
    // return all data
    if(action == "select" || action == "SELECT") {
        table = param.table;
        where_col = param.w_col;
        where_op = param.w_op;
        where_val = param.w_val;

        let result = getRecord(table, where_col, where_op, where_val);
        return createResponseFormat("ok", result);
    }
    
    // update specific record
    if(action == "update" || action == "UPDATE") {
        table = param.table;
        col_list = param.cols.split(",");
        col_dict = {};
        for(let i = 0; i < col_list.length; i++) {
            col_dict[col_list[i].trim()] = param[col_list[i].trim()];
        }
        where_col = param.w_col;
        where_op = param.w_op;
        where_val = param.w_val;

        let result = updateRecord(table, col_dict, where_col, where_op, where_val);
        return createResponseFormat("ok", result);
    }
}

// add record
function addRecord(table, col_dict) {
    let sheet = getSheet(table);
    let last_row = sheet.getLastRow();
    let last_col = sheet.getLastColumn();

    let new_row = [];
    for(let col in col_dict) {
        let sheet_headers = sheet.getRange(1, 1, 1, last_col).getValues()[0]
        let col_index = sheet_headers.indexOf(col);

        // 存在しなかった場合は新規追加（しなくてもいい？）
        if(col_index == -1) {
            sheet.getRange(1, sheet.getLastColumn() + 1).setValue(col);
            col_index = sheet.getLastColumn();
        }

        new_row[col_index] = col_dict[col];
    }
    sheet.appendRow(new_row);
}

// delete record
function deleteRecords(table, where_col, where_op, where_val) {
    let sheet = getSheet(table);
    let last_row = sheet.getLastRow();
    let last_col = sheet.getLastColumn();

    let sheet_headers = sheet.getRange(1, 1, 1, last_col).getValues()[0]
    let col_index = sheet_headers.indexOf(where_col);

    if(last_row == 1)
        return;

    let sheet_values = sheet.getRange(2, 1, last_row - 1, last_col).getValues();
    for(let i = sheet_values.length - 1; i >= 0; i--) {
        let row = sheet_values[i];
        if(where_op == "=" && row[col_index] == where_val) {
            sheet.deleteRow(i + 2);
        }
    }
}

// get record
function getRecord(table, where_col, where_op, where_val) {
    let sheet = getSheet(table);
    let last_row = sheet.getLastRow();
    let last_col = sheet.getLastColumn();

    let sheet_headers = sheet.getRange(1, 1, 1, last_col).getValues()[0]
    let col_index = sheet_headers.indexOf(where_col);

    if(last_row == 1)
        return [];

    let sheet_values = sheet.getRange(2, 1, last_row - 1, last_col).getValues();
    let result = [];
    for(let i = 0; i < sheet_values.length; i++) {
        let row = sheet_values[i];
        if(
            !where_op || // whereが指定されていない場合は全件返す
            (where_op == "=" && row[col_index] == where_val) // whereが指定されている場合は条件に合致するものだけ返す
        ) {
            let record = {};
            for(let j = 0; j < sheet_headers.length; j++) {
                record[sheet_headers[j]] = row[j];
            }
            result.push(record);
        }
    }
    return result;
}

// update record
function updateRecord(table, col_dict, where_col, where_op, where_val) {
    let sheet = getSheet(table);
    let last_row = sheet.getLastRow();
    let last_col = sheet.getLastColumn();

    let sheet_headers = sheet.getRange(1, 1, 1, last_col).getValues()[0]
    let col_index = sheet_headers.indexOf(where_col);

    if(last_row == 1)
        return [];

    let sheet_values = sheet.getRange(2, 1, last_row - 1, last_col).getValues();
    for(let i = 0; i < sheet_values.length; i++) {
        let row = sheet_values[i];
        if(where_op == "=" && row[col_index] == where_val) {
            for(let col in col_dict) {
                let sheet_headers = sheet.getRange(1, 1, 1, last_col).getValues()[0]
                let col_index = sheet_headers.indexOf(col);

                // 存在しなかった場合は新規追加（しなくてもいい？）
                if(col_index == -1) {
                    sheet.getRange(1, last_col + 1).setValue(col);
                    col_index = last_col;
                }

                sheet.getRange(i + 2, col_index + 1).setValue(col_dict[col]);
            }
        }
    }
}


// add flight data to sheet
function addFlightRecord(table, col_dict) {
    let sheet = getSheet(table);
    let last_row = sheet.getLastRow();
    let last_col = sheet.getLastColumn();

    let new_row = [];
    for(let col in col_dict) {
        let sheet_headers = sheet.getRange(1, 1, 1, last_col).getValues()[0]
        let col_index = sheet_headers.indexOf(col);

        // 存在しなかった場合は新規追加（しなくてもいい？）
        if(col_index == -1) {
            sheet.getRange(1, sheet.getLastColumn() + 1).setValue(col);
            col_index = sheet.getLastColumn();
        }

        new_row[col_index] = col_dict[col];
    }


    let date = Utilities.parseDate(new_row[1] + " " + new_row[5], "GMT", "dd MMM yyyy HH:mm");
    // GMT+9に変換
    // date.setTime(date.getTime() + 9 * 60 * 60 * 1000);

    // let new_date = Intl.DateTimeFormat('ja-JP').format(date);
    let new_date = date.getFullYear() + "/" + (date.getMonth() + 1) + "/" + date.getDate() + " " + Utilities.formatDate(date, "JST", "EEE");
    let new_time = date.getHours() + ":" + Utilities.formatDate(date, "JST", "mm");

    new_row[1] = new_date;
    new_row[5] = new_time;
    // new_row[1] = Utilities.parseDate(new_row[1], "GMT", "dd MMM yyyy")
    // let new_date = new_row[1].toDateString()
    // 一行目だった時だけ重複処理しない
    if(last_row > 1)
    {
      // 既に同じdate, flightのデータがある場合は無視
      let sheet_values = sheet.getRange(2, 1, last_row - 1, last_col).getValues();
      for(let i = 0; i < sheet_values.length; i++) {
          let row = sheet_values[i];
          let row_date = row[1]//.toDateString()
          let row_time = row[5].getHours() + ":" + Utilities.formatDate(row[5], "JST", "mm");
          if(new_row.length < 3) return; // date, flightがない場合は無視
          if(row[2] == new_row[2] && row_date == new_date && row_time == new_time) {
              return;
          }
      }
    }
    sheet.appendRow(new_row);
}

// fetch flight data from flightradars24
function fetchFlightData() {
    let url = "https://www.flightradar24.com/data/aircraft/ja607a";
    let response = UrlFetchApp.fetch(url);
    
    let records = [];
    let html = response.getContentText();

    var $ = Cheerio.load(html);

    // get flight data
    let flight_data = $("table tbody tr");
    flight_data.each(function(i, elem) {
        let record = {};
        let tds = $(this).find("td");
        record['id'] = Utilities.getUuid(); // id
        record['date'] = $(tds[2]).text().trim(); // date
        record['flight'] = $(tds[5]).text().trim(); // flight
        record['from'] = $(tds[3]).text().trim(); // from
        record['to'] = $(tds[4]).text().trim(); // to
        record['std'] = $(tds[7]).text().trim(); // std
        records.push(record);
    });

    return records.reverse();
}

// 未来分を推測する
function predictFlightData() {
    let sheet = getSheet("飛行履歴");
    let last_row = sheet.getLastRow();
    let last_col = sheet.getLastColumn();
    let sheet_values = sheet.getRange(2, 1, last_row - 1, last_col).getValues();

    let last_date = sheet_values[sheet_values.length - 1][1];
    // 最新日は除外する
    let records = sheet_values.filter(record => record['date'] != last_date);

    return records;
}


// run daily scheduled script
function runDailyScheduledScript() {
    updateFlightData();
}

// test predict flight data
function testPredictFlightData() {
    let testData = predictFlightData();
    debugger;
}

// update flight data
function updateFlightData() {
    let records = fetchFlightData();
    for(let i = 0; i < records.length; i++) {
        addFlightRecord("飛行履歴", records[i]);
    }
}

// test update flight data
function testUpadteFlightData() {
    updateFlightData();
    debugger;
}

// test fetch flight data
function testFetchFlightData() {
    let testData = fetchFlightData();
    debugger;
}

// test function
function testAddFlightRecord() {
    addFlightRecord("飛行履歴", {
        "id": Utilities.getUuid(),
        "date": "14 Nov 2023",
        "flight": "HD29",
        "from": "HND",
        "to": "CTS",
    });
}


// response builder
function createResponseFormat(type, records) {
    let resData = {
        status: type,
        records,
    }
    let out = ContentService.createTextOutput(JSON.stringify(resData));
    out.setMimeType(ContentService.MimeType.JSON);
  
    return out;
}
  
function createResponseSucceed() { return createResponseFormat("ok"); }

// get String
function getEnv(key) { return PropertiesService.getScriptProperties().getProperty(key);}


// get Sheet
function getSheet(name) { return SpreadsheetApp.getActiveSpreadsheet().getSheetByName(name); }
