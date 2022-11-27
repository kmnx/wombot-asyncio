import anyio, asynctelnet
from anyio import connect_tcp


async def shell(tcp):
    async with asynctelnet.TelnetClient(tcp, client=True) as stream:
        gotstatus = False
        while gotstatus is False:
            statusreq = bytearray('input.harbor_0.status\n','utf-8')
            await stream.send(statusreq)
            outp = await stream.receive(1024)
            if not outp:
                # End of File
                status = None
                break
            elif 'connected' in str(outp,'utf-8'):
                gotstatus = True    
                status = str(outp,'utf-8')
            # display all server output
            # print(str(outp,'utf-8'), flush=True)

        return status

    # EOF
    print()

async def main():
    async with await connect_tcp('localhost', 1234) as client:
        status = await shell(client)
        print(status)
        return status
        
#anyio.run(main)

