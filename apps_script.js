/**
 * Shunyalabs TTS Test Report — Google Apps Script
 *
 * SETUP:
 * 1. Open your Google Sheet
 * 2. Go to Extensions > Apps Script
 * 3. Delete any existing code, paste this entire file
 * 4. Click Deploy > Manage deployments > Edit > New version > Deploy
 * 5. Copy the URL into .env as APPS_SCRIPT_URL=<url>
 *
 * HOW IT WORKS:
 *   POST  → pushes test results + uploads audio to Drive + creates links in sheet
 *   GET   → returns editable inputs from "Inputs" sheet as JSON
 *
 * Audio files are saved to a shared "TTS_Test_Audio" folder in Google Drive.
 * Anyone with the sheet link can click and listen to the audio output.
 */

// ===== GET: Return test inputs from the "Inputs" sheet =====

function doGet(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var ws = ss.getSheetByName("Inputs");

    if (!ws) {
      return ContentService.createTextOutput(
        JSON.stringify({ success: false, error: "No 'Inputs' sheet found. Run a POST first to create it." })
      ).setMimeType(ContentService.MimeType.JSON);
    }

    var data = ws.getDataRange().getValues();
    var inputs = {};
    for (var i = 3; i < data.length; i++) {
      var section = String(data[i][0]).trim();
      var key     = String(data[i][1]).trim();
      var subKey  = String(data[i][2]).trim();
      var voice   = String(data[i][3]).trim();
      var text    = String(data[i][4]).trim();

      if (!section || !key) continue;
      if (!inputs[section]) inputs[section] = {};

      if (subKey) {
        if (!inputs[section][key]) inputs[section][key] = {};
        inputs[section][key][subKey] = (subKey === "voice") ? voice : text;
      } else if (voice) {
        inputs[section][key] = { voice: voice, text: text };
      } else {
        inputs[section][key] = text;
      }
    }

    return ContentService.createTextOutput(
      JSON.stringify({ success: true, inputs: inputs })
    ).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ success: false, error: err.toString() })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}


// ===== Audio folder in Google Drive =====

function getAudioFolder() {
  var folderName = "TTS_Test_Audio";
  var folders = DriveApp.getFoldersByName(folderName);
  var folder;
  if (folders.hasNext()) {
    folder = folders.next();
  } else {
    folder = DriveApp.createFolder(folderName);
  }
  // Make folder accessible to anyone with link
  folder.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  return folder;
}

function uploadAudio(folder, testId, audioB64, mime, format) {
  var ext = {
    "audio/mpeg": "mp3", "audio/wav": "wav", "audio/pcm": "pcm",
    "audio/ogg": "ogg", "audio/flac": "flac", "audio/basic": "raw"
  }[mime] || format || "mp3";

  var fileName = testId + "." + ext;

  // Delete old file with same name if exists
  var existing = folder.getFilesByName(fileName);
  while (existing.hasNext()) {
    existing.next().setTrashed(true);
  }

  var blob = Utilities.newBlob(Utilities.base64Decode(audioB64), mime, fileName);
  var file = folder.createFile(blob);
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

  return file.getId();
}


// ===== POST: Push test results + upload audio + populate Inputs sheet =====

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();

    // ---- Handle audio batch upload (phase 2) ----
    if (data.action === "upload_audio") {
      return handleAudioUpload(ss, data);
    }

    var runTime = data.run_time || new Date().toISOString();
    var results = data.results || [];
    var summary = data.summary || {};
    var cats = data.categories || [];
    var inputsData = data.inputs || null;

    // ---- Sheet 1: Test Results ----
    var ws = getOrCreateSheet(ss, "Test Results");
    ws.clear();

    ws.getRange("A1").setValue("Shunyalabs TTS SDK - Test Report | Run: " + runTime)
      .setFontSize(14).setFontWeight("bold");

    var headers = [
      "Test ID", "Category", "Sub-Category", "Test Name", "Description",
      "Input Text", "Input Config",
      "Status", "Latency (ms)", "Audio Size (bytes)", "Audio Duration (s)",
      "Output Format", "Audio Link",
      "Error", "Notes",
      "Updated At"
    ];
    var headerRow = 3;
    var headerRange = ws.getRange(headerRow, 1, 1, headers.length);
    headerRange.setValues([headers]);
    headerRange.setFontWeight("bold")
      .setBackground("#333333")
      .setFontColor("#FFFFFF")
      .setHorizontalAlignment("center");

    if (results.length > 0) {
      var dataRange = ws.getRange(headerRow + 1, 1, results.length, headers.length);
      dataRange.setValues(results.map(function(r) {
        return [
          r.test_id || "",
          r.category || "",
          r.subcategory || "",
          r.test_name || "",
          r.description || "",
          r.input_text || "",
          r.input_config || "",
          r.status || "",
          r.duration_ms || "",
          r.audio_bytes || "",
          r.audio_duration_sec || "",
          r.output_format || "",
          "",  // Audio Link — filled by audio batch upload
          r.error_message || "",
          r.notes || "",
          r.timestamp || ""
        ];
      }));

      // Color status cells (column H = 8)
      for (var i = 0; i < results.length; i++) {
        var cell = ws.getRange(headerRow + 1 + i, 8);
        var status = results[i].status;
        if (status === "PASS") {
          cell.setBackground("#c8edc8").setFontWeight("bold");
        } else if (status === "FAIL") {
          cell.setBackground("#f2c2c2").setFontWeight("bold");
        } else if (status === "ERROR") {
          cell.setBackground("#ffd9a6").setFontWeight("bold");
        }
      }

      // Wrap input text column for readability
      ws.getRange(headerRow + 1, 6, results.length, 1).setWrap(true);
      ws.setColumnWidth(6, 300);  // Input Text wider
      ws.setColumnWidth(7, 250);  // Input Config wider
      ws.setColumnWidth(13, 100); // Audio Link

      // Summary row
      var summaryRow = headerRow + 1 + results.length + 1;
      ws.getRange(summaryRow + 1, 4).setValue("TOTAL").setFontWeight("bold");
      ws.getRange(summaryRow + 1, 5).setValue(results.length + " tests");
      ws.getRange(summaryRow + 1, 8).setValue(
        "P:" + summary.passed + " F:" + summary.failed +
        " E:" + summary.errors + " S:" + summary.skipped
      ).setFontWeight("bold");
      ws.getRange(summaryRow + 1, 9).setValue(summary.total_ms || "");
      ws.getRange(summaryRow + 1, 16).setValue(runTime).setFontWeight("bold");
    }

    var autoResizeCols = [1,2,3,4,5,8,9,10,11,12,14,15,16];
    for (var ac = 0; ac < autoResizeCols.length; ac++) {
      ws.autoResizeColumn(autoResizeCols[ac]);
    }

    // ---- Sheet 2: Summary ----
    var ws2 = getOrCreateSheet(ss, "Summary");
    ws2.clear();

    ws2.getRange("A1").setValue("Test Summary | " + runTime)
      .setFontSize(14).setFontWeight("bold");

    var sumHeaders = ["Category", "Total", "Pass", "Fail", "Error", "Pass Rate", "Avg Latency (ms)", "Updated At"];
    var sumHeaderRange = ws2.getRange(3, 1, 1, sumHeaders.length);
    sumHeaderRange.setValues([sumHeaders]);
    sumHeaderRange.setFontWeight("bold")
      .setBackground("#333333")
      .setFontColor("#FFFFFF")
      .setHorizontalAlignment("center");

    if (cats.length > 0) {
      var catRange = ws2.getRange(4, 1, cats.length, sumHeaders.length);
      catRange.setValues(cats.map(function(c) {
        return [c.name, c.total, c.pass, c.fail, c.error, c.pass_rate, c.avg_latency, runTime];
      }));

      for (var j = 0; j < cats.length; j++) {
        var rateCell = ws2.getRange(4 + j, 6);
        if (cats[j].pass_rate === "100%") {
          rateCell.setBackground("#c8edc8").setFontWeight("bold");
        } else if (cats[j].pass === 0) {
          rateCell.setBackground("#f2c2c2").setFontWeight("bold");
        } else {
          rateCell.setBackground("#fff3cd").setFontWeight("bold");
        }
      }

      var overallRow = 4 + cats.length + 1;
      ws2.getRange(overallRow, 1).setValue("OVERALL").setFontWeight("bold");
      ws2.getRange(overallRow, 2).setValue(summary.total || 0).setFontWeight("bold");
      ws2.getRange(overallRow, 3).setValue(summary.passed || 0).setFontWeight("bold");
      ws2.getRange(overallRow, 4).setValue(summary.failed || 0).setFontWeight("bold");
      ws2.getRange(overallRow, 5).setValue(summary.errors || 0).setFontWeight("bold");
      var overallRate = summary.total > 0
        ? Math.round(summary.passed / summary.total * 100) + "%"
        : "N/A";
      ws2.getRange(overallRow, 6).setValue(overallRate).setFontWeight("bold");
      ws2.getRange(overallRow, 7).setValue(summary.total_ms || "").setFontWeight("bold");
      ws2.getRange(overallRow, 8).setValue(runTime).setFontWeight("bold");

      if (overallRate === "100%") {
        ws2.getRange(overallRow, 1, 1, sumHeaders.length).setBackground("#c8edc8");
      }
    }

    for (var c2 = 1; c2 <= sumHeaders.length; c2++) {
      ws2.autoResizeColumn(c2);
    }

    // ---- Sheet 3: Inputs (editable by user) ----
    if (inputsData) {
      populateInputsSheet(ss, inputsData);
    }

    return ContentService.createTextOutput(
      JSON.stringify({ success: true, rows: results.length, audio_uploaded: 0 })
    ).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ success: false, error: err.toString() })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}


// ===== Handle batched audio uploads (phase 2) =====

function handleAudioUpload(ss, data) {
  var audioFiles = data.audio_files || [];
  var audioFolder = getAudioFolder();
  var audioLinks = {};
  var uploaded = 0;

  for (var i = 0; i < audioFiles.length; i++) {
    var af = audioFiles[i];
    try {
      var fileId = uploadAudio(audioFolder, af.test_id, af.audio_b64, af.audio_mime || "audio/mpeg", af.output_format);
      audioLinks[af.test_id] = "https://drive.google.com/file/d/" + fileId + "/view";
      uploaded++;
    } catch (err) {
      audioLinks[af.test_id] = "upload error: " + err.toString();
    }
  }

  // Update Audio Link column (M = 13) in Test Results sheet
  var ws = ss.getSheetByName("Test Results");
  if (ws) {
    var headerRow = 3;
    var lastRow = ws.getLastRow();
    if (lastRow > headerRow) {
      var testIds = ws.getRange(headerRow + 1, 1, lastRow - headerRow, 1).getValues();
      for (var r = 0; r < testIds.length; r++) {
        var tid = String(testIds[r][0]).trim();
        if (audioLinks[tid] && audioLinks[tid].indexOf("http") === 0) {
          var cell = ws.getRange(headerRow + 1 + r, 13);
          cell.setFormula('=HYPERLINK("' + audioLinks[tid] + '", "▶ Play")');
          cell.setFontColor("#1a73e8").setFontWeight("bold");
        }
      }
    }
  }

  return ContentService.createTextOutput(
    JSON.stringify({ success: true, audio_uploaded: uploaded, audio_links: audioLinks })
  ).setMimeType(ContentService.MimeType.JSON);
}


// ===== Populate the "Inputs" sheet with editable test inputs =====

function populateInputsSheet(ss, inputsData) {
  var ws = getOrCreateSheet(ss, "Inputs");
  ws.clear();

  ws.getRange("A1").setValue("Edit test inputs below. Changes will be picked up on next test run.")
    .setFontSize(12).setFontWeight("bold").setFontColor("#1a73e8");
  ws.getRange("A1:E1").merge();

  var headers = ["Section", "Key", "Sub-Key", "Voice", "Text"];
  var headerRange = ws.getRange(3, 1, 1, headers.length);
  headerRange.setValues([headers]);
  headerRange.setFontWeight("bold")
    .setBackground("#333333")
    .setFontColor("#FFFFFF")
    .setHorizontalAlignment("center");

  var rows = [];

  var batch = inputsData.batch || {};
  for (var bid in batch) {
    rows.push(["batch", bid, "", batch[bid].voice || "", batch[bid].text || ""]);
  }

  var stream = inputsData.streaming || {};
  for (var sid in stream) {
    rows.push(["streaming", sid, "", stream[sid].voice || "", stream[sid].text || ""]);
  }

  var voices = inputsData.voices || {};
  for (var lang in voices) {
    rows.push(["voices", lang, "", "", voices[lang] || ""]);
  }

  var simples = ["formats", "speed", "silence", "normalization", "timestamps", "background"];
  for (var si = 0; si < simples.length; si++) {
    var sec = simples[si];
    if (inputsData[sec] && inputsData[sec].text) {
      rows.push([sec, "text", "", "", inputsData[sec].text]);
    }
  }

  var exprs = inputsData.expressions || {};
  for (var expr in exprs) {
    rows.push(["expressions", expr, "", "", exprs[expr] || ""]);
  }

  var ec = inputsData.edge_cases || {};
  for (var ecid in ec) {
    rows.push(["edge_cases", ecid, "", ec[ecid].voice || "", ec[ecid].text || ""]);
  }

  if (rows.length > 0) {
    ws.getRange(4, 1, rows.length, 5).setValues(rows);

    var sectionColors = {
      "batch": "#e8f5e9", "streaming": "#e3f2fd", "voices": "#fff3e0",
      "formats": "#f3e5f5", "speed": "#fce4ec", "expressions": "#e0f7fa",
      "silence": "#f1f8e9", "normalization": "#fbe9e7", "timestamps": "#e8eaf6",
      "background": "#efebe9", "edge_cases": "#fff8e1"
    };

    for (var r = 0; r < rows.length; r++) {
      var section = rows[r][0];
      if (sectionColors[section]) {
        ws.getRange(4 + r, 1, 1, 5).setBackground(sectionColors[section]);
      }
    }

    ws.getRange(4, 5, rows.length, 1).setWrap(true);
    ws.setColumnWidth(5, 500);
    ws.setColumnWidth(1, 120);
    ws.setColumnWidth(2, 120);
    ws.setColumnWidth(3, 80);
    ws.setColumnWidth(4, 120);
  }

  var protection = ws.getRange("A1:E3").protect();
  protection.setDescription("Headers - do not edit");
  protection.setWarningOnly(true);

  ws.autoResizeColumn(1);
  ws.autoResizeColumn(2);
}


function getOrCreateSheet(ss, name) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
  }
  return sheet;
}
