from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.cache import add_never_cache_headers
import json


def get_datatables_records(request, querySet, columnIndexNameMap, jsonTemplatePath = None, *args):
    """
    Usage:
        querySet: query set to draw data from.
        columnIndexNameMap: field names in order to be displayed.
        jsonTemplatePath: optional template file to generate custom json from.
        If not provided it will generate the data directly from the model.
    """
    #Gets the number of columns
    cols = int(request.GET.get('iColumns', 0))

    #Safety measure.If someone messes with iDisplayLength manually, we clip it to the max value of 100.
    iDisplayLength = min(int(request.GET.get('iDisplayLength', 10)), 100)

    #Where the data starts from (page)
    startRecord = int(request.GET.get('iDisplayStart', 0))

    #Where the data ends (end of page)
    endRecord = startRecord + iDisplayLength

    # Pass sColumns
    keys = columnIndexNameMap.keys()
    keys.sort()
    colitems = [columnIndexNameMap[key] for key in keys]
    sColumns = ",".join(map(str,colitems))

    # Ordering data
    iSortingCols = int(request.GET.get('iSortingCols', 0))
    asortingCols = []

    if iSortingCols:
        for sortedColIndex in range(0, iSortingCols):
            sortedColID = int(request.GET.get('iSortCol_'+str(sortedColIndex), 0))
            #Makes sure the column is sortable first
            if request.GET.get('bSortable_{0}'.format(sortedColID), 'false') == 'true':
                sortedColName = columnIndexNameMap[sortedColID]
                sortingDirection = request.GET.get('sSortDir_'+str(sortedColIndex), 'asc')

                if sortingDirection == 'desc' and not sortedColName.startswith('-'):
                    sortedColName = '-' + sortedColName
                elif sortedColName.startswith('-') and sortingDirection == 'asc':
                    sortedColName = sortedColName[1:]

                asortingCols.append(sortedColName)
        querySet = querySet.order_by(*asortingCols)

    #Determines which columns are searchable
    searchableColumns = []
    for col in range(0, cols):
        if request.GET.get('bSearchable_{0}'.format(col), False) == 'true':
            searchableColumns.append(columnIndexNameMap[col])

    #Applies filtering by value sent by user
    customSearch = request.GET.get('sSearch', '').encode('utf-8')
    if customSearch != '':
        outputQ = None
        first = True
        for searchableColumn in searchableColumns:
            kwargz = {searchableColumn+"__icontains" : customSearch}
            outputQ = outputQ | Q(**kwargz) if outputQ else Q(**kwargz)
        querySet = querySet.filter(outputQ)

    # Individual column search
    outputQ = None
    for col in range(0,cols):
        if request.GET.get('sSearch_{0}'.format(col), False) > '' and \
                        request.GET.get('bSearchable_{0}'.format(col), False) == 'true':
            kwargz = {columnIndexNameMap[col]+"__icontains" : request.GET['sSearch_{0}'.format(col)]}
            outputQ = outputQ & Q(**kwargz) if outputQ else Q(**kwargz)

    if outputQ:
        querySet = querySet.filter(outputQ)

    #Counts how many records match the final criteria
    iTotalRecords = iTotalDisplayRecords = querySet.count()

    #Gets the slice
    querySet = querySet[startRecord:endRecord]

    #Required echo response
    sEcho = int(request.GET.get('sEcho', 0))

    if jsonTemplatePath:
        #Prepares the JSON with the response, consider using : from django.template.defaultfilters import escapejs
        jsonString = render_to_string(jsonTemplatePath, locals())

        response = HttpResponse(jsonString, mimetype="application/javascript")
    else:
        aaData = []
        queryset_values = querySet.values()
        for queryset_row in queryset_values:
            rowkeys = queryset_row.keys()
            rowvalues = queryset_row.values()
            rowlist = []
            for col in range(0, len(colitems)):
                for idx, val in enumerate(rowkeys):
                    if val == colitems[col]:
                        rowlist.append(unicode(rowvalues[idx]))
            aaData.append(rowlist)

        response_dict = {
            'aaData': aaData,
            'sEcho': sEcho,
            'iTotalRecords': iTotalRecords,
            'iTotalDisplayRecords': iTotalDisplayRecords,
            'sColumns': sColumns
        }

        response = HttpResponse(json.dumps(response_dict), mimetype='application/javascript')
    #prevent from caching datatables result
    add_never_cache_headers(response)
    return response