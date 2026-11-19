# RELAP Automation Tools

## RELAP_generate
`RELAP_generate.py` generates RELAP files based on a provided jinja2 template, excel workbook filepath, and the name of a specific sheet in that workbook. These must be specified in the `configs` directory. The user may create as many YAML files as desired, as a GUI provides the ability to select between these files. See `template/test.j2`, `configs/example.yaml`, `example.xlsx`, and `DO_NOT_EDIT.i` (the desired output) for an example of how everything works together. 

### Usage
Run `python RELAP_generate.py` and select the desired configuration. The user may also include a custom note if desired. The generated RELAP file is stored in a directory called `runs`. `test.j2` includes a header that stores the details regarding its generation. 

## jinja_generate
`jinja_generate.py` is meant as a help in generating jinja2 templates to match an existing RELAP file. Following is an example of converting a couple of lines of a RELAP file:

### Usage
The line desired to be converted is the following:
```
*          Ebt       Pres       Temp     Qual
1020200    003       2.0e5      923.15   0.0
```

Only the variables `Pres`, `Temp`, and `Qual` are desired to be relplaced. 

1. Run `python jinja_generate.py`. 
2. The command line will ask for the object code, which is in this case "102" for the "Core Lower Plenum". Enter the code.
3. The command line will ask for the parameter names, space separated. One way to do this is to copy the parameters above: "Pres       Temp     Qual"
4. The command line will ask for ouputs in the desired format. Copy the applicable lines above: "2.0e5      923.15   0.0"
5. The terminal will then output the proper jinja string: 
```
{{ c102.Pres | relap_sci(11, 1, 'e') }}{{ "%-9.2f" | format(c102.Temp)}}{{ "%-3.1f" | format(c102.Qual)}}
```
6. The user may then paste this into the jinja template so that this portion of the .j2 file becomes:
```
*          Ebt       Pres       Temp     Qual
1020200    003       {{ c102.Pres | relap_sci(11, 1, 'e') }}{{ "%-9.2f" | format(c102.Temp)}}{{ "%-3.1f" | format(c102.Qual)}}
```
7. The terminal then prompts the user whether they would like to convert another line. If yes, the process repeats, but the user may change the object code or keep the current one. 

