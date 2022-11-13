from email import message


# from sympy import residue
#from app import transporter
#from tabulate import tabulate
from app.delivery import blueprint
from flask_restful import Resource, Api
from flask import jsonify, render_template, redirect, request, url_for
import json
#from app.base.util import verify_pass
#from app.models import audit, bag, depotomaster, depovendor, sku, auditsku, bagtosku, audittobag, disttobag, pickup, picktobag, deviatedbag, userinfo
#from app import db
#from app.models import depoinventory, deviateddepobag, depopickup
import datetime

#from app import mail

from flask_mail import Message

# function to return the data for screen1 

@blueprint.route('/get_delivery_order',methods=['GET','POST'])
def get_delivery_order():
    data = request.get_json(force=True)
    # exception handling for reading input parameters
    try:
        dispatch_date = data["dispatch_date"]
        if dispatch_date == "" or dispatch_date == None:
            return jsonify(status=400,message="Please Select Dispatch Date!")
    except:
        return jsonify(status=400,message="Please Select Dispatch Date!")
    try:
        customer_code = data["customer_code"]
        if customer_code == "" or customer_code == None:
            return jsonify(status=400,message="Please Select Customer Code!")
    except:
        return jsonify(status=400,message="Please Select Customer Code!")
    try:
        transporter = data["transporter"]
        if transporter == "" or transporter == None:
            return jsonify(status=400,message="Please Select Transporter Code!")
    except:
        return jsonify(status=400,message="Please Select Transporter Code!")
    try:
        order_number = data["order_number"]
        if order_number == "" or order_number == None:
            return jsonify(status=400,message="Please Select Order Number!")
    except:
        return jsonify(status=400,message="Please Select Order Number!")
    # exception handling done for reading input parameters
    # print([dispatch_date,customer_code,transporter,order_number])

    import pyodbc
    cnxn = pyodbc.connect(driver='{FreeTDS}', host='115.124.119.236', database='NALCO_DISPATCH',
                      trusted_connection='no', user='Aipalatte2', password='guest2@Nalco2022',
                      TrustServerCertificate='yes')
    cursor = cnxn.cursor()
    sql_query = """ 
        select *
        from QN_Tbl_Sales_Order_HDR
        INNER JOIN QN_Tbl_Sales_Order_Transporter_Detail
        ON ( QN_Tbl_Sales_Order_Transporter_Detail.Sales_Order_Number = QN_Tbl_Sales_Order_HDR.Sales_Order_Number)
        WHERE QN_Tbl_Sales_Order_HDR.Plan_Delivery_Date = '{0}' AND Customer_Code = '{1}'
        AND QN_Tbl_Sales_Order_HDR.Sales_Order_Number = '{2}'
        AND QN_Tbl_Sales_Order_Transporter_Detail.Transporter_code = '{3}'
            """.format(dispatch_date,customer_code,order_number,transporter)
    
    cursor.execute(sql_query) 
    columns = [column[0] for column in cursor.description]
    results = []
    main_results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    for temp in results:
    # print(type(temp['Plan_Delivery_Date']))
    # print(temp['Plan_Delivery_Date'])
        temp_obj  = {}
        temp_obj['delivery_date'] = temp['Plan_Delivery_Date'].strftime("%d-%m-%Y")
        temp_obj['order_number'] = temp['Sales_Order_Number']
        temp_obj['customer_code'] = temp['Customer_Code']
        temp_obj['customer_name'] = temp['Customer_Name']
        temp_obj['destination'] = temp['Destination']
        temp_obj['transporter_name'] = temp['Transporter_Name']
        temp_obj['transporter_code'] = temp['Transporter_Code']
        temp_obj['delivery_quantity'] = temp['Plan_Del_Qty']
        main_results.append(temp_obj)
    # print(main_results)
    return jsonify(status=200,message="This is the Test API! Yeah it's workingss!!",data=main_results)


# function to return the data for screen2

@blueprint.route('/get_delivery_order_details',methods=['GET','POST'])
def get_delivery_order_details():
    data = request.get_json(force=True)
    # exception handling for reading input parameters
    try:
        order_number = data["order_number"]
        if order_number == "" or order_number == None:
            return jsonify(status=400,message="Please Select Order Number!")
    except:
        return jsonify(status=400,message="Please Select Order Number!")
    import pyodbc
    cnxn = pyodbc.connect(driver='{FreeTDS}', host='115.124.119.236', database='NALCO_DISPATCH',
                      trusted_connection='no', user='Aipalatte2', password='guest2@Nalco2022',
                      TrustServerCertificate='yes')
    cursor = cnxn.cursor()
    sql_query = """ 
        select * from 
            QN_Tbl_Sales_Order_Detail where Sales_Order_Number = '{0}'
            """.format(order_number)
    cursor.execute(sql_query) 
    columns = [column[0] for column in cursor.description]
    results = []
    main_results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    for temp in results:
        temp_obj = {}
        temp_obj['order_number'] = temp['Sales_Order_Number']
        temp_obj['line_item_number'] = temp['Line_item_Number']
        temp_obj['material_code'] = temp['Material_Code']
        temp_obj['material_description'] = temp['Material_Name']
        temp_obj['quantity'] = temp['Quantity']
        main_results.append(temp_obj)
    print(main_results)
    return jsonify(status=200,message="This is the Test API! Yeah it's workingss!!",data=main_results)


#function to get the data for screen

@blueprint.route('/get_truck_planning_orders',methods=['GET','POST'])
def get_truck_planning_orders():
    data = request.get_json(force=True)
    # exception handling for reading input parameters
    try:
        dispatch_date = data["dispatch_date"]
        if dispatch_date == "" or dispatch_date == None:
            return jsonify(status=400,message="Please Select Dispatch Date!")
    except:
        return jsonify(status=400,message="Please Select Dispatch Date!")
    try:
        customer_code = data["customer_code"]
        if customer_code == "" or customer_code == None:
            return jsonify(status=400,message="Please Select Customer Code!")
    except:
        return jsonify(status=400,message="Please Select Customer Code!")
    import pyodbc
    cnxn = pyodbc.connect(driver='{FreeTDS}', host='115.124.119.236', database='NALCO_DISPATCH',
                      trusted_connection='no', user='Aipalatte2', password='guest2@Nalco2022',
                      TrustServerCertificate='yes')
    cursor = cnxn.cursor()
    sql_query = """ 
        select *
        from QN_Tbl_Sales_Order_HDR
        INNER JOIN QN_Tbl_Sales_Order_Detail
        ON ( QN_Tbl_Sales_Order_Detail.Sales_Order_Number = QN_Tbl_Sales_Order_HDR.Sales_Order_Number)
        WHERE QN_Tbl_Sales_Order_HDR.Plan_Delivery_Date = '{0}' AND Customer_Code = '{1}'
            """.format(dispatch_date, customer_code)
    cursor.execute(sql_query) 
    columns = [column[0] for column in cursor.description]
    results = []
    main_results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    for temp in results:
        temp_obj = dict()
        temp_obj["order_number"] = temp["Sales_Order_Number"]
        temp_obj["line_item_number"] = temp["Line_item_Number"]
        temp_obj["material_code"] = temp["Material_Code"]
        temp_obj["material_description"] = ""
        temp_obj["weight"] = temp["Net_Weight"]
        temp_obj["uom"] = temp["UOM"]
        temp_obj["quantity"] = temp["Quantity"]
        main_results.append(temp_obj)
    return jsonify(status=200,message="This is the Test API! Yeah it's workingss!!",data=main_results)




