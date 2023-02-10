orders = {"name=Esmeli%20Catering&location=Assessors%20Block%20Lot&items=Tacos:1,Burritos:2","name=HALAL%20FOOD&location=532%20MARKET%20ST&items=Chicken%20Gyro:1","name=FLAVORS%20OF%20AFRICA&location=405%20HOWARD%20ST&items=Meat%20And%20Vegi%20Rice%20Bowls:1,Drinks%20And%20Juices:1","name=El%20Gallo%20Jiro&location=3055%2023RD%20ST&items=Burritos:1,Quesadillas:1","name=Street%20Meet&location=777%20MARIPOSA%20ST&items=Tortas:1","name=Boulangerie%20La%20Camionnette&location=500%20FLORIDA%20ST&items=Bread:1,Coffee:2","name=Halal%20Cart%20of%20San%20Francisco&location=1%20MARKET%20ST&items=Gyro:2","name=Munch%20India&location=400%20CALIFORNIA%20ST&items=Poultry:1,Seafood:1"}


foodItems = {"burgers", "tacos", "pizza", "sandwich", "water"}



sessionCoockie = getCookie()



getCookie = function()
    headers = {}
    headers["Content-Type"] = "application/json"
    body = ''
    return wrk.format("POST", "/login?username=user&password=1234" , headers, body)
end



request1 = function()
    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Cookie"]="session=" .. sessionCoockie
    body = ''
    return wrk.format("POST", "/saveOrder?" .. orders[math.random(#orders)] , headers, body)
end

request2 = function()
    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Cookie"]="session=" .. sessionCoockie
    body = ''
    return wrk.format("GET", "/search?q=" .. foodItems[math.random(#foodItems)] , headers, body)
end


requests = {}
requests[0] = request1
requests[1] = request1
requests[2] = request2
requests[3] = request2

request = function()
    return requests[math.random(0, 3)]()
end

response = function(status, headers, body)
    if status ~= 200 then
        io.write("------------------------------\n")
        io.write("Response with status: ".. status .."\n")
        io.write("------------------------------\n")
        io.write("[response] Body:\n")
        io.write(body .. "\n")
    end
end




