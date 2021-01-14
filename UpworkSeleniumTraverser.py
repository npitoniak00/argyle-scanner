from ArgyleUserRecordTemplate import ArgyleUserRecord

class UpworkSeleniumTraverser :

  def __init__(self,upwork_uname,upwork_pword,upwork_secondary_auth_answer,is_headless=False) :
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    print("UpworkSeleniumTraverser object initialized")
    # initialize selenium in headless or browser mode depending on init var
    selenium_init_options = Options()
    if is_headless :
      selenium_init_options.headless = True
    self.selenium_web_driver = webdriver.Firefox(options=selenium_init_options)
    # initialize instance variables
    self.upwork_uname = upwork_uname
    self.upwork_pword = upwork_pword
    self.upwork_secondary_auth_answer = upwork_secondary_auth_answer
    self.scraped_data = {"freelancer expertise categories":[],"profile settings data":{},"contact info":{}}
    self.load_local_config_json_data()
    self.profile_settings_html = ""
    self.main_portal_html = ""

  def set_main_portal_html(self,main_portal_html) : self.main_portal_html = main_portal_html
  def set_profile_settings_html(self,profile_settings_html) : self.profile_settings_html = profile_settings_html

  def get_main_portal_html(self) : return self.main_portal_html
  def get_profile_settings_html(self) : return self.profile_settings_html
  def get_scraped_data(self) : return self.scraped_data

  def load_local_config_json_data(self) :
    import json
    # load config file detaling the upwork interface components for simple workflow editing, as the programmer of this tool noticed the element identifiers change
    with open('upwork_selenium_config.json', 'r') as cf :
      data = cf.read().replace('\n', '')
      data = data.replace("{upwork_uname}",self.upwork_uname)
      data = data.replace("{upwork_pword}",self.upwork_pword)
      data = data.replace("{upwork_secondary_auth_answer}",self.upwork_secondary_auth_answer)
      self.config = json.loads(data)

  def does_interface_contain_necessary_components(self,interface_name) :
    from selenium.webdriver.common.by import By
    if interface_name not in self.config["interfaces"] : return False
    ret_components = []
    # attempt to access each required interface component and return bool depending if all elements are accessible
    for index,component in enumerate(self.config["interfaces"][interface_name]["required components"]) :
      # the primary authentication splits the login process into multiple distinct subviews, thus only the first two components may be assessed
      if interface_name == "primary authentication" and index > 1 : continue
      try :
        if component["identifier type"] == "id" : ret_components.append({"component":self.selenium_web_driver.find_element_by_id(component["identifier name"]),"component schema":component})
        elif component["identifier type"] == "class" : ret_components.append({"components":self.selenium_web_driver.find_elements_by_class_name(component["identifier name"]),"component schema":component})
        elif component["identifier type"] == "text" : ret_components.append({"component":self.selenium_web_driver.find_element_by_link_text(component["identifier name"]),"component schema":component})
        elif component["identifier type"] == "obscure text" : ret_components.append({"component":self.selenium_web_driver.find_element(By.CSS_SELECTOR,"[{}={}]".format(component["custom attr name"],component["custom attr value"])),"component schema":component})
        else : return False
      except Exception as ex :
        print(ex)
        return False
    return ret_components

  def operate_components_on_web_driver(self,interface_name) :
    import time
    import random
    from selenium.webdriver.common.by import By
    # traverse required components list, interacting with each as specified by the config file
    for index,component in enumerate(self.config["interfaces"][interface_name]["required components"]) :
      print("about to perform {} on element {} of type {}".format(component["action"],component["identifier name"],component["identifier type"]))
      # capture ui component with driver by either id or class name
      if component["identifier type"] == "id" : captured_component = self.selenium_web_driver.find_element_by_id(component["identifier name"])
      elif component["identifier type"] == "class" : captured_component = self.selenium_web_driver.find_element_by_class_name(component["identifier name"])
      elif component["identifier type"] == "text" : captured_component = self.selenium_web_driver.find_element_by_link_text(component["identifier name"])
      elif component["identifier type"] == "obscure text" : captured_component = self.selenium_web_driver.find_element(By.CSS_SELECTOR,"[{}={}]".format(component["custom attr name"],component["custom attr value"]))
      # perform appropriate action on the given resource as specified in the config file
      if component["action"] == "populate input" : captured_component.send_keys(component["value"])
      elif component["action"] == "click" : captured_component.click()
      # halt program execution to enable interface re-rendering, and imitate non-automated human behavior
      time.sleep(random.randint(2,4))

  def pass_main_authentication(self) :
    self.selenium_web_driver.get("https://www.upwork.com/ab/account-security/login")
    interface_name = "primary authentication"
    # check that all required interface elements are present for processing
    initial_component_existence_scan = self.does_interface_contain_necessary_components(interface_name)
    if initial_component_existence_scan == False : return False
    # attempt to interact with components iteratively to step through the authentication process
    try :
      self.operate_components_on_web_driver(interface_name)
      # check if secondary authorization components are present, if so redirect control flow to handle it
      time.sleep(10)
      print("running secondary authentication")
      secondary_auth_component_existence_scan = self.does_interface_contain_necessary_components("secondary authentication")
      if secondary_auth_component_existence_scan :
        secondary_authentication_process = self.pass_secondary_authentication()
        if secondary_authentication_process == False : return False
    except :
      # attempt to solve secondary authentication with different tags
      print("running secondary authentication variant")
      try :
        secondary_auth_component_existence_scan = self.does_interface_contain_necessary_components("secondary authentication variant")
        print("secondary auth varient existence scan: {}".format(secondary_auth_component_existence_scan))
        if secondary_auth_component_existence_scan :
          secondary_authentication_process = self.pass_secondary_authentication_variant()
          print("secondary auth variant process: {}".format(secondary_authentication_process))
          if secondary_authentication_process == False : return False
      except : return False
    return True

  def pass_secondary_authentication(self) :
    interface_name = "secondary authentication"
    # check if secondary device authentication interface is encountered
    secondary_auth_component_existence_scan = self.does_interface_contain_necessary_components(interface_name)
    if secondary_auth_component_existence_scan == False : return False
    try : self.operate_components_on_web_driver(interface_name)
    except : return False
    return True

  def pass_secondary_authentication_variant(self) :
    interface_name = "secondary authentication variant"
    # check if secondary device authentication interface is encountered
    secondary_auth_component_existence_scan = self.does_interface_contain_necessary_components(interface_name)
    if secondary_auth_component_existence_scan == False : return False
    try : self.operate_components_on_web_driver(interface_name)
    except : return False
    return True

  def move_to_view_profile_from_main_portal(self) :
    # check that the current interface is main portal which contains the proper link to the view profile
    main_portal_component_existence = self.does_interface_contain_necessary_components("main portal")
    if main_portal_component_existence == False : return False
    # click navigation button to move view to main profile
    try : self.operate_components_on_web_driver("main portal")
    except : return False
    # check if secondary authorization components are present, if so redirect control flow to handle it
    secondary_auth_component_existence_scan = self.does_interface_contain_necessary_components("secondary authentication")
    if secondary_auth_component_existence_scan :
      secondary_authentication_process = self.pass_secondary_authentication()
      if secondary_authentication_process == False : return False
    return True

  def move_to_contact_info(self) :
    import time
    self.selenium_web_driver.get("https://www.upwork.com/ab/account-security/device-authorization?szRedir=https%3A%2F%2Fwww.upwork.com%2Ffreelancers%2Fsettings%2FcontactInfo")
    time.sleep(3)
    # check if secondary authorization components are present, if so redirect control flow to handle it
    secondary_auth_component_existence_scan = self.does_interface_contain_necessary_components("secondary authentication")
    if secondary_auth_component_existence_scan :
      secondary_authentication_process = self.pass_secondary_authentication()
      if secondary_authentication_process == False : return False
    return True

  def record_contact_info(self) :
    import re
    import time
    # process contact info interface
    time.sleep(10)
    contact_info_component_existence = self.does_interface_contain_necessary_components("contact info")
    if contact_info_component_existence == False : return False
    try :
      for index,component in enumerate(contact_info_component_existence) :
        if component["component schema"]["identifier type"] != "obscure text" : continue
        preliminary_parse = component["component"].get_attribute("innerHTML").replace("\n","").strip()
        # remove commas
        no_commas = re.sub(',','',preliminary_parse)
        # remove any embedded html tags
        remove_tags_re = re.compile('<.*?>')
        no_tags = re.sub(remove_tags_re,'',no_commas)
        # remove redundant whitespace
        no_redundant_spaces = re.sub(' +',' ',no_tags)
        self.scraped_data["contact info"][component["component schema"]["custom attr value"]] = no_redundant_spaces
      return True
    except Exception as ex :
      print(ex)
      return False
    return True

  def record_view_profile(self) :
    interface_name = "profile settings"
    import time
    time.sleep(15)
    # check if profile settings required components are present, indicating a proper view transition
    view_profile_component_existence = self.does_interface_contain_necessary_components(interface_name)
    if view_profile_component_existence == False : return False
    self.set_profile_settings_html(self.selenium_web_driver.page_source)
    # attempt to parse the profile settings code for the various profile values
    return self.parse_profile_settings_code()

  def record_main_portal(self) :
    interface_name = "main portal"
    import time
    # wait for the components to load
    time.sleep(15)
    # check that current interface is main portal
    main_portal_component_existence = self.does_interface_contain_necessary_components(interface_name)
    if main_portal_component_existence == False : return False
    self.set_main_portal_html(self.selenium_web_driver.page_source)
    # read and parse the required component data for the config-specified data fields to read
    try :
      for index,component in enumerate(main_portal_component_existence) :
        if component["component schema"]["identifier type"] != "class" : continue
        for index,sub_component in enumerate(component["components"]) :
          self.scraped_data["freelancer expertise categories"].append(sub_component.get_attribute("innerHTML"))
      return True
    except Exception as ex :
      print(ex)
      return False

  def parse_profile_settings_code(self) :
    import json
    try :
      profile_data = self.get_profile_settings_html()
      code_lines = profile_data.split("\n")
      for line in code_lines :
        if "var phpVars" in line :
          isolate_json = json.loads(line.strip().split("= ")[1].replace(";",""))
          self.scraped_data["profile settings data"]["uid"] = isolate_json["profileSettings"]["userId"]
          self.scraped_data["profile settings data"]["first name"] = isolate_json["profileSettings"]["firstName"]
          self.scraped_data["profile settings data"]["last name"] = isolate_json["profileSettings"]["lastName"]
          self.scraped_data["profile settings data"]["client name"] = isolate_json["profileSettings"]["clientName"]
          self.scraped_data["profile settings data"]["employment history"] = isolate_json["profileSettings"]["profile"]["employmentHistory"]
          self.scraped_data["profile settings data"]["competencies"] = isolate_json["profileSettings"]["profile"]["competencies"]
          self.scraped_data["profile settings data"]["availability"] = isolate_json["profileSettings"]["profile"]["availability"]
          self.scraped_data["profile settings data"]["languages"] = isolate_json["profileSettings"]["profile"]["languages"]
          self.scraped_data["profile settings data"]["education"] = isolate_json["profileSettings"]["profile"]["education"]
          return True
    except Exception as ex :
      print(ex)
      return False

  def execute_site_traversal_and_data_recording(self) :
    print("about to pass main authentication")
    print(self.pass_main_authentication())

    print("about to record portal interface")
    print(self.record_main_portal())

    print("about to move to view profile")
    print(self.move_to_view_profile_from_main_portal())

    print("about to move to view profile")
    print(self.record_view_profile())

    print("about to move to contact info")
    print(self.move_to_contact_info())

    print("about to record contact info")
    print(self.record_contact_info())

    print("dump info below")
    print(self.get_scraped_data())

  def record_session_record(self) :
    user_data = {
      'id':'124324234',
      'account':'',
      'employer':'US unemployment',
      'full_name':'Nicholas Pitoniak',
      'first_name':'Jim',
      'last_name':'Smith',
      'email':'npitoniak@gmail.com',
      'phone_number':'7177798154',
      'birth_date':'03/27/1998',
      'picture_url':'test photo url',
      'ssn':'777777777',
      'marital_status':'single',
      'gender':'male',
      'address':{"line1":"frustration st.","line2":"jaja","city":"york","state":"PA","postal_code":"17403","country":"PA"}
    }
    try:
        record = ArgyleUserRecord(**user_data)
        serialized = record.json()
    except ValidationError as e:
        print(e.json())
