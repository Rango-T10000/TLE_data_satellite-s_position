import os
from datetime import datetime, timezone, timedelta
import urllib.request
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv

def generate_csv(sat, time, eol_index, us_inc, num_samples, data):
    output_directory = "/home2/wzc/starlink/tle/output"
    output_filename = sat.strip() + "-" + \
            time.strftime("%Y_%m_%d_%H_%M_%S_%f") + "-" + str(us_inc) \
            + "-" + str(num_samples) + ".csv"
    output_filename = output_filename.replace(" ", "_").replace("(", "_")\
            .replace(")", "_").replace("/", "_")\
            .replace("[", "_").replace("]", "_")
    
    output_path = os.path.join(output_directory, output_filename)
    outfile = open(output_path, "w")

    line1_index = eol_index + 1
    line2_index = eol_index + 71

    line1 = data[line1_index:line1_index+70]
    line2 = data[line2_index:line2_index+70]

    satellite = twoline2rv(line1, line2, wgs84)

    for i in range(num_samples):
        datestamp = time.strftime("%Y,%m,%d,%H,%M,%S.%f")

        second = float(str(time.second) + "." + str(time.microsecond))

        position, v = satellite.propagate(time.year, time.month, time.day, \
                time.hour, time.minute, second)

        position_string = ","
        if (position[0] > 0):
            position_string += " "
        position_string += str(position[0]) + ","

        while len(position_string) < 16:
            position_string += " "

        if (position[1] > 0):
            position_string += " "

        position_string += str(position[1]) + ","

        while len(position_string) < 31:
            position_string += " "

        if (position[2] > 0):
            position_string += " "

        position_string += str(position[2])

        outfile.write(datestamp + position_string + "\n")

        time = time + timedelta(microseconds=us_inc)

    outfile.close()

def main():
    # url = raw_input("Enter TLE url: ")
    # try:
    #     response = urllib2.urlopen(url)
    #     data = response.read()
    # except:
    #     print "  \033[31mError fetching specified TLE file\033[0m"
    #     exit(1)

    #如果已经下好了.txt下面就这样，没下好或者要下新的那就取消下方注释
    #这样为了防止多次运行代码，被网站拒绝访问
    #如果网站拒绝访问出现403，那就自己自行下载.txt文件，后面读取这个.txt文件就就行了

    # # 下载TLE文件
    # tle_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
    tle_file = "/home2/wzc/starlink/tle/starlink.txt"
    # urllib.request.urlretrieve(tle_url, tle_file)

    # # 下载TLE数据，如果文件不存在或超过一天
    # file_exists = os.path.exists(tle_file)
    # file_is_old = (datetime.now(timezone.utc) - datetime.fromtimestamp(os.path.getmtime(tle_file), timezone.utc)).total_seconds() > 86400

    # if not file_exists or file_is_old:
    #     urllib.request.urlretrieve(tle_url, tle_file)

    # 打开文件并读取其内容
    with open(tle_file, "r") as file:
        data = file.read()
    
    sat = input("Enter satellite name (blank=all): ").rstrip()

    name_index = data.find(sat.strip())
    eol_index = data.find("\n", name_index)

    if sat.strip() == "":
        print("  \033[36mUsing all satellites in supplied TLE\033[0m")
    else:
        if name_index == -1 or eol_index == -1:
            print( "  \033[31mNo match for " + sat + " in TLE specified\033[0m")
            exit(1)

    start = input("Enter start date and time (UTC, blank=system time) " \
            + "(YYYY MM DD HH MM SS MICROS): ")

    if start.strip() == "":
        time = datetime.now(timezone.utc)
        print( "  \033[36mUsing current system time (UTC): " \
                + time.isoformat(' ') + "\033[0m")
    else:
        try:
            time = datetime.strptime(start.strip(), "%Y %m %d %H %M %S %f")
            print( "  \033[36mParsed start time as: " + time.isoformat(' ') \
                    + "\033[0m")
        except:
            print( "  \033[31mUnable to parse start time from: " + start)
            print( "        example of suitable input: " \
                    + "2019 01 09 22 05 16 01\033[0m")
            exit(1)

    inc_field = input("Enter field to be incremented [hr, min, sec, us]: ")

    try:
        inc = int(input("Enter incrementation value: "))
    except:
        print( "  \033[31mUnable to parse value\033[0m")
        exit(1)

    us_inc = inc

    if inc_field.strip() == "hr":
        us_inc = us_inc * 3.6e9

        print( "  \033[36mEach time step will increase by " + str(inc) \
                + " hour(s) (" + str(us_inc) + "μs)\033[0m")
    elif inc_field.strip() == "min":
        us_inc = us_inc * 6e7

        print( "  \033[36mEach time step will increase by " + str(inc) \
                + " minute(s) (" + str(us_inc) + "μs)\033[0m")
    elif inc_field.strip() == "sec":
        us_inc = us_inc * 1e6

        print( "  \033[36mEach time step will increase by " + str(inc) \
                + " second(s) (" + str(us_inc) + "μs)\033[0m")
    elif inc_field.strip() == "us":
        print( "  \033[36mEach time step will increase by " + str(us_inc) \
                + "μs\033[0m")
    else:
        print( "  \033[31mUnable to parse time increment field\033[0m")
        exit(1)

    try:
        num_samples = int(\
                input("Enter total number of samples: "))
    except:
        print( "  \033[31mUnable to parse value\033[0m")
        exit(1)

    if sat.strip() != "":
        generate_csv(sat, time, eol_index, us_inc, num_samples, data)
    else:
        print( "\nGetting all SVs")

        while(eol_index < len(data)):
            sat = data[(eol_index-25):eol_index].strip()

            generate_csv(sat, time, eol_index, us_inc, num_samples, data)

            eol_index = eol_index + 71 + 71 + 23

            print( '.',)

    print( "\n\n\033[1;32mFinished\033[0m")


#代码从这里开始运行
main()

#ECEF坐标（Earth-Centered, Earth-Fixed）指的是用于表示地球表面或附近位置的笛卡尔坐标系。
#在ECEF坐标系中，地球的中心是原点（0, 0, 0），三个坐标轴与地球的旋转轴和赤道面对齐。
#X轴指向本初子午线（0度经度）和赤道的交点。Y轴指向东经90度和赤道的交点。Z轴垂直于地球表面，指向北极。