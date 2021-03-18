<!DOCTYPE html>
<html>

<head>
    <title>My first Chartist Tests</title>
    <link rel="stylesheet"
          href="/app/bower_components/chartist/dist/chartist.min.css">
</head>

<body>
    <!-- Site content goes here !-->
    <script src="/app/bower_components/chartist/dist/chartist.min.js"></script>
    <script src="/app/bower_components/jquery/dist/jquery.min.js"></script>

    {{.HTMLContent}}
    <script>
    {{.Script}}
    </script>
</body>

</html>