<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "dbcontacts";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$action = isset($_GET['action']) ? $_GET['action'] : 'save';
$student = null;
$found = false;

// If naka submit na
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $studno = $_POST['studno'] ?? '';
    $name = $_POST['name'] ?? '';
    $cpno = $_POST['cpno'] ?? '';
    $currentAction = $_POST['action'];

    if ($currentAction == 'save') {
        $sql = "INSERT INTO tblsms (studno, name, cpno) VALUES ('$studno', '$name', '$cpno')";
        if ($conn->query($sql) === TRUE) {
            echo "<script>alert('New record created successfully!'); window.location.href='?action=save';</script>";
            exit();
        } else {
            echo "Error: " . $sql . "<br>" . $conn->error;
        }
    } elseif ($currentAction == 'update') {
        $sql = "UPDATE tblsms SET name='$name', cpno='$cpno' WHERE studno='$studno'";
        if ($conn->query($sql) === TRUE) {
            echo "<script>alert('Record updated successfully!'); window.location.href='?action=save';</script>";
            exit();
        } else {
            echo "Error updating record: " . $conn->error;
        }
    } elseif ($currentAction == 'delete') {
        $sql = "DELETE FROM tblsms WHERE studno='$studno'";
        if ($conn->query($sql) === TRUE) {
            echo "<script>alert('Record deleted successfully!'); window.location.href='?action=save';</script>";
            exit();
        } else {
            echo "Error deleting record: " . $conn->error;
        }
    } elseif ($currentAction == 'search') {
        $sql = "SELECT * FROM tblsms WHERE studno='$studno'";
        $result = $conn->query($sql);
        if ($result->num_rows > 0) {
            $student = $result->fetch_assoc();
            $found = true;
            $action = $_GET['action'];
        } else {
            echo "<script>alert('Student not found!');</script>";
        }
    }
}

$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Records</title>
    <link href="conDes.css" rel="stylesheet">
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .form-container { max-width: 400px; margin: auto; }
        .action-links { margin-bottom: 20px; }
        .action-links a { margin-right: 10px; text-decoration: none; color: blue; }
        input, button { width: 100%; padding: 10px; margin: 5px 0; }
        button { cursor: pointer; }
    </style>
    <script>
        function updateSubmitButtonText() {
            const action = new URLSearchParams(window.location.search).get('action');
            const submitButton = document.querySelector('#submitButton');
            if (submitButton) {
                if (action === 'save') {
                    submitButton.textContent = 'Save';
                } else if (action === 'update') {
                    submitButton.textContent = 'Update';
                } else if (action === 'delete') {
                    submitButton.textContent = 'Delete';
                }
            }
        }

        window.onload = updateSubmitButtonText;
    </script>
</head>
<body>

<div class="form-container">
    <div class="action-links">
        <a href="?action=save">Add New</a>
        <a href="?action=update">Update</a>
        <a href="?action=delete">Delete</a>
    </div>

    <form method="POST" action="?action=<?= $action ?>">
        <label>Student Number:</label>
        <input type="text" name="studno" placeholder="ex. 25-140432" value="<?= $student['studno'] ?? '' ?>" required>

        <label>Name:</label>
        <input type="text" name="name" 
            value="<?= $student['name'] ?? '' ?>" 
            <?= ($action == 'save' || ($action == 'update' && $found)) ? '' : 'readonly' ?> required>

        <label>CP No:</label>
        <input type="number" name="cpno" 
            value="<?= $student['cpno'] ?? '' ?>" 
            <?= ($action == 'save' || ($action == 'update' && $found)) ? '' : 'readonly' ?> required>

        <input type="hidden" name="action" id="hiddenAction" value="<?= $action ?>">

        <?php if ($action == 'update' || $action == 'delete'): ?>
            <?php if (!$found): ?>
                <button type="submit" name="action" value="search">Search</button>
            <?php else: ?>
                <button id="submitButton" type="submit"><?= ucfirst($action) ?></button>
            <?php endif; ?>
        <?php else: ?>
            <button id="submitButton" type="submit">Save</button>
        <?php endif; ?>
    </form>
</div>

</body>
</html>
