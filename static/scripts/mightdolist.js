document.querySelector('#addtask').addEventListener('click', function () {
    // close modal
    $('#exampleModal').modal('hide');
    // get values
    var task = document.querySelector('#task').value;
    document.querySelector('#task').value = '';
    if (task) {
        $.post('/addtask', { task: task }, function (data, status) {
            if (status == 'success') {
                // add task to table
                var table = document.querySelector('#taskstable');
                var row = table.insertRow(1);
                var cell1 = row.insertCell(0);
                var cell2 = row.insertCell(1);
                cell1.innerHTML = task;
                cell2.innerHTML = `
                            <div class="form-check">
                                <input class="form-check-input taskcheckbox" type="checkbox" value="" id="${data.task_id}">
                            </div>
                            `
            }
        });
    }
});

document.querySelectorAll(".taskcheckbox").forEach(function (element) {
    element.addEventListener('click', function () {
        event.preventDefault();
        var task_id = element.id;
        var done = element.checked;
        $.post('/updatetask', { task_id: task_id, done: done }, function (data, status) {
            if (status == 'success') {
                console.log("updated");
                // toggle checkbox
                element.checked = !element.checked;
                var description_td = document.getElementById("task_" + task_id);
                if (element.checked) {
                    description_td.style.textDecoration = "line-through";
                }
                else {
                    description_td.style.textDecoration = "none";
                }
            }
        });
    });
});
