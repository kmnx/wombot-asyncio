import anyio, asynctelnet
from anyio import connect_tcp


async def shell(tcp):
    async with asynctelnet.TelnetClient(tcp, client=True) as stream:
        print('try')
        #print(stream)
        gotstatus = False
        while gotstatus is False:
            # read stream until '?' mark is found
            print('lets await stream')
            #helpstr = 'help'.encode('UTF-8')
            # thisis = await stream.send(helpstr)
            #print(helpstr)
            helptwo = bytearray('input.harbor_0.status\n','utf-8')
            await stream.send(helptwo)
            outp = await stream.receive(1024)
            print(outp)
            print('awaited outp')
            if not outp:
                # End of File
                print('no outp')
                break
            elif 'connected' in str(outp,'utf-8'):
                # reply all questions with 'y'.
                print('we have outp')
                print(str(outp,'utf-8'))
                gotstatus = True    
                status = str(outp,'utf-8')
                return status
            print('gotstatus is ',gotstatus)
            # display all server output
            print(str(outp,'utf-8'), flush=True)

    # EOF
    print()

async def main():
    async with await connect_tcp('localhost', 1234) as client:
        await shell(client)
anyio.run(main)

