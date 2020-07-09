// API Cloudconvert
// Конвертация и выгрузка в zip архиве все шаблонов в рамках темы
const scale = 0.5;
const api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjM2YTYxYTZmYjZiYjg2OGExMzA5OTQ0MjNjZGU4YTJiNzBkMjAxNDk0NDlkMDM4NjFmNTkyMzZmNzJlNWQxMjYyODUzMzE2OTEyN2Y4ODY5In0.eyJhdWQiOiIxIiwianRpIjoiMzZhNjFhNmZiNmJiODY4YTEzMDk5NDQyM2NkZThhMmI3MGQyMDE0OTQ0OWQwMzg2MWY1OTIzNmY3MmU1ZDEyNjI4NTMzMTY5MTI3Zjg4NjkiLCJpYXQiOjE1ODk0ODgwMjAsIm5iZiI6MTU4OTQ4ODAyMCwiZXhwIjo0NzQ1MTYxNjE5LCJzdWIiOiI0MjM4MTI1NCIsInNjb3BlcyI6WyJ1c2VyLnJlYWQiLCJ1c2VyLndyaXRlIiwidGFzay5yZWFkIiwidGFzay53cml0ZSIsIndlYmhvb2sucmVhZCIsIndlYmhvb2sud3JpdGUiLCJwcmVzZXQucmVhZCIsInByZXNldC53cml0ZSJdfQ.gXSBOUmfpPybNHa5XAo7LbQz92GWaDsHAoezMnYiC10E2ZNUs-HhF4jKXEUpvwCc8o--WmIlnC818UE9REX_V2Duw5xmMkK-5rYW4jirqvHrU-7eKlthuI8iIdLV4mv9V3Q3nmsZg6V0IQ9zw5xWi2pXfIEJhWs5k4TwOgCPVfAfDWlvnW0mzBXhtwhMvJQ1hRj-49Fb4Su2QZ1n6onZSbexVrtcZqf8kRVv04DqKeE9T4KhGlAOFJJUCoJSiTj3w07oiS_6mPQV3nRersubjTMLpLxgwOurJWzHf6KzeoMnjVZY9ixXISGbWYSjZWdYPP1-dX6k_r6iYlp1Bmj1rFQYR8Lid5_L26Gs9XtXA10XBRUtHtEL2PCB1GJSR1EwEB6cQ5N3Zq_iwal9a6wt6tiVh_Nbj-iggna7ifgO7E55yVGNvDAL9xKVZIUFvh_B6_wfUNvNFl_pNPzUzBjH1vEYVJ2XItHOlMM5RthD-7Gy8iKDsrK53RP9BXCK168tl3e58JPDJUQ0DCxxtwsOCiw8VAQQ6c-5BLMIOTl7bMguTgxlXUD4fOYk1k5Ea9Nq5nD7X0oQrn-KOQUkONobejGoVPV2ODwSL3W558qG0nWmZlxRGGhX48l5Z0Dq2d2rgT4MWOltDo36wyE87RpSd8eoidxTqXZ-oBHJ2JbtBTQ"
const px_cm = 37.7952755905511;
let fileLinks = [];
let fileFormat = ''


function create_zip() {
    let i;
    let zip = new JSZip();
    let count = 0

    for (i = 0; i < fileLinks.length; i++) {
        // console.log(fileLinks[i])
        JSZipUtils.getBinaryContent(fileLinks[i], function (err, data) {
            count++
            if (err) {
                console.error("Problem happened when download: ", err)
            } else {
                zip.file(`template_${count}.${fileFormat}`, data)
            }
            if (count === fileLinks.length) {
                zip.generateAsync({type: "blob"})
                    .then(function (content) {
                        saveAs(content, "templates.zip");
                    })
                    .then(() => {
                        fileLinks = []
                        $('.main-svg-container ._fade').remove()
                        $('#off-canvas-1 ._fade').remove()
                        $('button.save-button-menu').attr('disabled', false)
                    })
            }
        });
    }
    // очищаем
}


function get_ids() {
    let ids_nodes = []
    return ids_nodes
}

function addFileUrl(url, svg, count) {
    if (!svg) {
        fileLinks.push(url)
    } else {
        sendJob($('<div></div>'), 'svg', false, url, count)
    }
    if (fileLinks.length === count) {
        create_zip()
    }
}

function import_file(format, pdf_url) {
    if (format === 'svg') {
        return {
            filename: "x.pdf",
            operation: "import/url",
            url: pdf_url,
        }
    } else {
        return {
            operation: "import/upload"
        }
    }
}

function waitTask(task_id, svg, count) {
    $.ajax({
        url: `https://api.cloudconvert.com/v2/tasks/${task_id}/wait`,
        headers: {'Authorization': `Bearer ${api_key}`,},
        async: true,
        success: function (response) {
            addFileUrl(response.data.result.files[0].url, svg, count);
        },
        error: function (error) {
            alert('error AJAX WAIT TASK ' + error)
        }
    });
}

function sendFormToUpload(template, task, width_cm, height_cm, format) {
    let upload_form_data = task.result.form
    const formData = new FormData();
    for (const parameter in upload_form_data.parameters) {
        formData.append(parameter, upload_form_data.parameters[parameter]);
    }

    if (format === 'pdf') {
        template.css('width', `${width_cm}cm`)
        template.css('height', `${height_cm}cm`)
    }

    // .html() берет все что внутри, мы хотим взять все. поэтому оборачиваем
    let _template = template.wrapAll('<div>').parent()

    let content = _template.html().replace(/transform:/g, '-webkit-transform:')
    if (_template.find('body').length === 0) {
        content = `<body style="margin: 0">${content}</body>`
    }

    const r = Math.random().toString(36).substring(7);
    let blob = new File([content], `${r}.html`, {type: "text/html"})
    formData.append("file", blob)
    let request = new XMLHttpRequest();
    request.open("POST", upload_form_data.url);
    request.setRequestHeader('Authorization', `Bearer ${api_key}`);
    request.responseType = "json";
    request.send(formData);
}

function sendJob(template, format, svg, pdf_url, count) {
    fileFormat = format

    let width = parseInt(template.css('width'), 10)
    let height = parseInt(template.css('height'), 10)

    let width_cm = (width / px_cm)
    let height_cm = (height / px_cm)

    width_cm = parseInt(width_cm * 10) / 10
    height_cm = parseInt(height_cm * 10) / 10


    const config_convert = {
        'pdf': {
            'operation': 'convert',
            'input': 'import-my-file',
            'output_format': 'pdf',
            'engine': 'chrome',
            "margin_top": 0,
            "margin_left": 0,
            "margin_bottom": 0,
            "margin_right": 0,
            "smart_shrinking": false,
            "page_width": width_cm,
            "page_height": height_cm,
            // "print_media_type": false,
        },
        'jpg': {
            'operation': 'convert',
            'input': 'import-my-file',
            'output_format': 'jpg',
            "engine": "chrome",
            "screen_width": width,
            "screen_height": height,
        },
        'png': {
            'operation': 'convert',
            'input': 'import-my-file',
            'output_format': 'png',
            "engine": "chrome",
            "screen_width": width,
            "screen_height": height,
        },
        'svg': {
            "engine": "mupdf",
            "input": 'import-my-file',
            "input_format": "pdf",
            "operation": "convert",
            "output_format": "svg",
            "text_to_path": true,
        }
    }

    let tasks = {};
    tasks['import-my-file'] = import_file(format, pdf_url)
    tasks['convert-my-file'] = config_convert[format]

    tasks['export-my-file'] = {
        'operation': 'export/url',
        'input': 'convert-my-file',
    }
    $.ajax({
        url: 'https://api.cloudconvert.com/v2/jobs',
        type: 'post',
        data: JSON.stringify({tasks: tasks}),
        contentType: 'application/json; charset=utf-8',
        async: true,
        headers: {'Authorization': `Bearer ${api_key}`,},
        dataType: 'json',
        success: function (response) {
            if (format !== 'svg') {
                sendFormToUpload(template, response.data.tasks[0], width_cm, height_cm, format)
                waitTask(response.data.tasks[2].id, svg, count)
            } else {
                waitTask(response.data.tasks[2].id, svg, count)
            }
        }
    });
}

function OnConvert(format, svg, goal) {
    let ids_nodes = [];
    if (goal === 'active_screen') {
        ids_nodes.push(saver_user_progress.getActiveScreenID())
    }
    if (goal === 'changed_screen') {
        ids_nodes.push($('.data_data').data('changed_screen_id'))
    }
    if (goal === 'all_screen') {
        ids_nodes = Array.from($('.data_data').data('ids_project_screens'))
    }
    if (ids_nodes.length > 0) {
        const fade = $('._fade').clone()
        fade.css('display', 'block')
        fade.appendTo('.main-svg-container')
        fade.appendTo('#off-canvas-1')
        $('button.save-button-menu').attr('disabled', true)

    }

    console.log(ids_nodes)
    const csrf_token = $("input[name=csrfmiddlewaretoken]").val();
    ids_nodes.forEach((id, index, array) => {
        let data = {
            csrfmiddlewaretoken: csrf_token,
            screen_id: id,
        }
        $.post(`/screen/get_screen`, data, (response) => {
            sendJob($(response['screen_html']), format, svg, '', array.length)
        }, 'json')
    })
}


(function () {
    $('.save-button-menu').click((event) => {
        $('.dropdown-menu-save').toggleClass('show-block');
    });
})();