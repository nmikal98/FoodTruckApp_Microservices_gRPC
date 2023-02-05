names = { "Maverick", "Goose", "Viper", "Iceman", "Merlin", "Sundown", "Cougar", "Hollywood", "Wolfman", "Jester" }

request1 = function()
    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Cookie"]="session=eyJpZCI6MSwibG9nZ2VkaW4iOnRydWUsInVzZXJuYW1lIjoidXNlciJ9.Y9DeCQ.FCBOime8cS0_RomU8bhOBsWkK1A"
    body = ''
    return wrk.format("GET", "/search?q=tacos", headers, body)
end

request2 = function()
    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Cookie"]="session=eyJpZCI6MSwibG9nZ2VkaW4iOnRydWUsInVzZXJuYW1lIjoidXNlciJ9.Y9DeCQ.FCBOime8cS0_RomU8bhOBsWkK1A"
    body = ''
    return wrk.format("POST", "/saveOrder?name=Esmeli%20Catering&location=Assessors%20Block%20Lot&items=Tacos:1,Burritos:2", headers, body)
end

request3 = function()
    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Cookie"]="session=eyJpZCI6MSwibG9nZ2VkaW4iOnRydWUsInVzZXJuYW1lIjoidXNlciJ9.Y9DeCQ.FCBOime8cS0_RomU8bhOBsWkK1A"
    body = ''
    return wrk.format("GET", "/search?q=burgers", headers, body)
end

requests = {}
requests[0] = request1
requests[1] = request2
requests[2] = request3
requests[3] = request3

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