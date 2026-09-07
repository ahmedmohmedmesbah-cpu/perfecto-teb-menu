using System.Diagnostics;

static string? FindProjectRoot()
{
    var directory = new DirectoryInfo(AppContext.BaseDirectory);

    for (var depth = 0; directory is not null && depth < 6; depth++)
    {
        var mainFile = Path.Combine(directory.FullName, "main.py");
        var packageDir = Path.Combine(directory.FullName, "perfecto_cms");

        if (File.Exists(mainFile) && Directory.Exists(packageDir))
        {
            return directory.FullName;
        }

        directory = directory.Parent;
    }

    return null;
}

static IEnumerable<(string FileName, string Arguments)> PythonCommands(string mainFile)
{
    var envPython = Environment.GetEnvironmentVariable("PERFECTO_PYTHON");
    if (!string.IsNullOrWhiteSpace(envPython))
    {
        yield return (envPython, Quote(mainFile));
    }

    yield return ("pythonw", Quote(mainFile));
    yield return ("python", Quote(mainFile));
    yield return (@"C:\Users\mohamed\AppData\Local\Programs\Python\Python313\pythonw.exe", Quote(mainFile));
    yield return (@"C:\Users\mohamed\AppData\Local\Programs\Python\Python313\python.exe", Quote(mainFile));
    yield return ("py", "-3 " + Quote(mainFile));
}

static string Quote(string value)
{
    return "\"" + value.Replace("\"", "\\\"") + "\"";
}

var projectRoot = FindProjectRoot();
if (projectRoot is null)
{
    File.WriteAllText(
        Path.Combine(AppContext.BaseDirectory, "perfecto_launcher_error.txt"),
        "Could not find main.py and perfecto_cms next to this launcher.",
        System.Text.Encoding.UTF8
    );
    return 1;
}

var mainFile = Path.Combine(projectRoot, "main.py");
var failures = new List<string>();

foreach (var command in PythonCommands(mainFile))
{
    try
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = command.FileName,
            Arguments = command.Arguments,
            WorkingDirectory = projectRoot,
            UseShellExecute = false,
            CreateNoWindow = true,
        };

        Process.Start(startInfo);
        return 0;
    }
    catch (Exception ex)
    {
        failures.Add($"{command.FileName}: {ex.Message}");
    }
}

File.WriteAllText(
    Path.Combine(projectRoot, "perfecto_launcher_error.txt"),
    "Could not start Python for Perfecto CMS." + Environment.NewLine + string.Join(Environment.NewLine, failures),
    System.Text.Encoding.UTF8
);

return 1;
